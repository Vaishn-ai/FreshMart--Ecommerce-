from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartDetailView.as_view(), name="cart_detail"),
    path("add/", views.AddToCartView.as_view(), name="cart_add"),
    path("items/<uuid:item_id>/", views.UpdateCartItemView.as_view(), name="cart_item_update"),
    path("items/<uuid:item_id>/save-for-later/", views.SaveForLaterView.as_view(), name="cart_save_for_later"),
    path("clear/", views.ClearCartView.as_view(), name="cart_clear"),
    path("coupon/", views.ApplyCouponView.as_view(), name="cart_apply_coupon"),
]
