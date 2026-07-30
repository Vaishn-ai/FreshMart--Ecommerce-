import csv
from datetime import timedelta
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from orders.models import Order, OrderItem
from products.models import Product
from accounts.models import User

LOW_STOCK_THRESHOLD = 10


class IsAdminOnly(permissions.IsAdminUser):
    pass


class RevenueAnalyticsView(APIView):
    """Query params: ?days=30 (default 30)."""
    permission_classes = [IsAdminOnly]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        since = timezone.now() - timedelta(days=days)
        paid_orders = Order.objects.filter(created_at__gte=since, payment_status="paid")

        daily = (
            paid_orders.annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(revenue=Sum("total"), order_count=Count("id"))
            .order_by("date")
        )
        totals = paid_orders.aggregate(total_revenue=Sum("total"), total_orders=Count("id"))

        return Response({
            "range_days": days,
            "total_revenue": totals["total_revenue"] or 0,
            "total_orders": totals["total_orders"] or 0,
            "daily": list(daily),
        })


class SalesAnalyticsView(APIView):
    permission_classes = [IsAdminOnly]

    def get(self, request):
        status_breakdown = Order.objects.values("status").annotate(count=Count("id")).order_by("-count")
        payment_breakdown = Order.objects.values("payment_method").annotate(count=Count("id")).order_by("-count")
        best_selling = (
            OrderItem.objects.values("product__id", "product__name")
            .annotate(units_sold=Sum("quantity"), revenue=Sum(F("unit_price") * F("quantity")))
            .order_by("-units_sold")[:10]
        )
        return Response({
            "status_breakdown": list(status_breakdown),
            "payment_breakdown": list(payment_breakdown),
            "best_selling_products": list(best_selling),
        })


class CustomerAnalyticsView(APIView):
    permission_classes = [IsAdminOnly]

    def get(self, request):
        total_customers = User.objects.filter(is_staff=False).count()
        since_30d = timezone.now() - timedelta(days=30)
        new_customers_30d = User.objects.filter(is_staff=False, created_at__gte=since_30d).count()

        top_customers = (
            Order.objects.filter(payment_status="paid")
            .values("user__id", "user__email")
            .annotate(total_spent=Sum("total"), order_count=Count("id"))
            .order_by("-total_spent")[:10]
        )
        return Response({
            "total_customers": total_customers,
            "new_customers_last_30_days": new_customers_30d,
            "top_customers": list(top_customers),
        })


class InventoryView(APIView):
    permission_classes = [IsAdminOnly]

    def get(self, request):
        products = Product.objects.filter(is_active=True).values(
            "id", "name", "sku", "stock", "mrp", "discount_price", "category__name"
        )
        return Response(list(products))


class LowStockAlertsView(APIView):
    permission_classes = [IsAdminOnly]

    def get(self, request):
        threshold = int(request.query_params.get("threshold", LOW_STOCK_THRESHOLD))
        products = Product.objects.filter(is_active=True, stock__lte=threshold).values(
            "id", "name", "sku", "stock", "category__name"
        ).order_by("stock")
        return Response({"threshold": threshold, "count": products.count(), "products": list(products)})


class ExportOrdersCSVView(APIView):
    permission_classes = [IsAdminOnly]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="orders_export.csv"'
        writer = csv.writer(response)
        writer.writerow(["Order Number", "Customer", "Status", "Payment Status", "Payment Method", "Total", "Created At"])
        for o in Order.objects.select_related("user").all():
            writer.writerow([o.order_number, o.user.email, o.status, o.payment_status, o.payment_method, o.total, o.created_at])
        return response


class ExportProductsCSVView(APIView):
    permission_classes = [IsAdminOnly]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="products_export.csv"'
        writer = csv.writer(response)
        writer.writerow(["Name", "SKU", "Category", "MRP", "Discount Price", "Stock", "Rating"])
        for p in Product.objects.select_related("category").all():
            writer.writerow([p.name, p.sku, p.category.name, p.mrp, p.discount_price, p.stock, p.rating_avg])
        return response


class DashboardSummaryView(APIView):
    """Single endpoint powering the admin dashboard's home screen."""
    permission_classes = [IsAdminOnly]

    def get(self, request):
        today = timezone.now().date()
        return Response({
            "total_revenue": Order.objects.filter(payment_status="paid").aggregate(t=Sum("total"))["t"] or 0,
            "orders_today": Order.objects.filter(created_at__date=today).count(),
            "pending_orders": Order.objects.filter(status="pending").count(),
            "total_products": Product.objects.filter(is_active=True).count(),
            "low_stock_count": Product.objects.filter(is_active=True, stock__lte=LOW_STOCK_THRESHOLD).count(),
            "total_customers": User.objects.filter(is_staff=False).count(),
        })
