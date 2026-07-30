from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import OrderInvoiceView

router = DefaultRouter()
router.register("", views.OrderViewSet, basename="order")

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("<uuid:pk>/status/", views.AdminUpdateOrderStatusView.as_view(), name="order_admin_status"),
    path("", include(router.urls)),
    path("<uuid:pk>/invoice/",OrderInvoiceView.as_view(), name="order-invoice"),
]
