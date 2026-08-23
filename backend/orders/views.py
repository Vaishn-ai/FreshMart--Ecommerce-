from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Order
from .serializers import OrderSerializer, CheckoutSerializer
from .services import create_order_from_cart, CheckoutError, advance_order_status
from .invoice import generate_invoice_pdf


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            order = create_order_from_cart(
                user=request.user,
                address_id=data["address_id"],
                shipping_method=data["shipping_method"],
                payment_method=data["payment_method"],
            )
        except CheckoutError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.prefetch_related("items__product__images", "status_history").get(id=order.id)
        response_data = OrderSerializer(order, context={"request": request}).data
        # For online payment methods, the frontend follows up with the payments app
        # (/api/v1/payments/razorpay/create/ or /stripe/create-intent/) using this order id.
        response_data["requires_payment"] = order.payment_method in ("stripe", "razorpay", "upi")
        return Response(response_data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.prefetch_related("items__product__images", "status_history")
        if self.request.user.is_staff:
            return qs.all()
        return qs.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()

        print("Current Status:", order.status)

        if order.status in ("shipped", "delivered", "cancelled", "returned"):
            return Response(
                {"detail": f"Order cannot be cancelled once {order.status}."},
                status=400,
            )

        try:
            advance_order_status(
                order,
                "cancelled",
                note="Cancelled by customer",
            )
        except Exception as e:
            print("ERROR:", str(e))
            return Response(
                {"detail": str(e)},
                status=400,
            )

        return Response(
            OrderSerializer(
                order,
                context={"request": request},
            ).data
        )

    @action(detail=True, methods=["get"])
    def invoice(self, request, pk=None):
        order = self.get_object()
        buffer = generate_invoice_pdf(order)
        return FileResponse(buffer, as_attachment=True, filename=f"{order.order_number}-invoice.pdf")

    @action(detail=True, methods=["get"])
    def track(self, request, pk=None):
        order = self.get_object()
        return Response({
            "order_number": order.order_number,
            "status": order.status,
            "tracking_number": order.tracking_number,
            "timeline": [
                {"status": h.status, "note": h.note, "changed_at": h.changed_at}
                for h in order.status_history.all()
            ],
        })


class AdminUpdateOrderStatusView(APIView):
    """Admin-only — advance an order through packed/shipped/delivered/returned."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        order = get_object_or_404(Order.objects.prefetch_related("items__product__images", "status_history"), pk=pk)
        new_status = request.data.get("status")
        note = request.data.get("note", "")
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({"detail": "Invalid status."}, status=400)
        if new_status == "shipped":
            order.tracking_number = request.data.get("tracking_number", order.tracking_number)
            order.save(update_fields=["tracking_number"])
        advance_order_status(order, new_status, note=note)
        return Response(OrderSerializer(order, context={"request": request}).data)

class OrderInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            user=request.user
        )

        pdf = generate_invoice_pdf(order)

        return FileResponse(
            pdf,
            as_attachment=True,
            filename=f"Invoice-{order.order_number}.pdf",
            content_type="application/pdf",
        )