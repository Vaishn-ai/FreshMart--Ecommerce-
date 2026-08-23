from django.urls import path
from . import views

urlpatterns = [
    path("razorpay/create/<uuid:order_id>/", views.RazorpayCreateOrderView.as_view(), name="razorpay_create"),
    path("razorpay/verify/", views.RazorpayVerifyView.as_view(), name="razorpay_verify"),
    path("stripe/create-intent/<uuid:order_id>/", views.StripeCreateIntentView.as_view(), name="stripe_create_intent"),
    path("stripe/confirm/", views.StripeConfirmView.as_view(), name="stripe_confirm"),
    path("upi/initiate/", views.UpiInitiateView.as_view(), name="upi_initiate"),
]
