from django.urls import path
from . import views

urlpatterns = [
    path("", views.WishlistView.as_view(), name="wishlist"),
    path("<uuid:product_id>/", views.WishlistItemDetailView.as_view(), name="wishlist_item"),
    path("<uuid:product_id>/move-to-cart/", views.MoveToCartView.as_view(), name="wishlist_move_to_cart"),
]
