from django.urls import path
from . import views

urlpatterns = [
    path("summary/", views.DashboardSummaryView.as_view(), name="dashboard_summary"),
    path("analytics/revenue/", views.RevenueAnalyticsView.as_view(), name="analytics_revenue"),
    path("analytics/sales/", views.SalesAnalyticsView.as_view(), name="analytics_sales"),
    path("analytics/customers/", views.CustomerAnalyticsView.as_view(), name="analytics_customers"),
    path("inventory/", views.InventoryView.as_view(), name="inventory"),
    path("inventory/low-stock/", views.LowStockAlertsView.as_view(), name="low_stock_alerts"),
    path("export/orders.csv", views.ExportOrdersCSVView.as_view(), name="export_orders_csv"),
    path("export/products.csv", views.ExportProductsCSVView.as_view(), name="export_products_csv"),
]
