from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from categories.models import Category
from products.models import Product
from coupons.models import Coupon
from .models import Cart, CartItem


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="shopper", email="shopper@example.com", password="StrongPass123")
        self.client.force_authenticate(user=self.user)
        category = Category.objects.create(name="Snacks")
        self.product = Product.objects.create(
            name="Chips", category=category, mrp=Decimal("100.00"),
            discount_price=Decimal("80.00"), stock=10, sku="CHIPS-1",
        )

    def test_add_to_cart(self):
        response = self.client.post(reverse("cart_add"), {"product_id": str(self.product.id), "quantity": 2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["quantity"], 2)

    def test_add_to_cart_exceeding_stock_fails(self):
        response = self.client.post(reverse("cart_add"), {"product_id": str(self.product.id), "quantity": 999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cart_totals_calculation(self):
        self.client.post(reverse("cart_add"), {"product_id": str(self.product.id), "quantity": 3})
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.subtotal, Decimal("240.00"))

    def test_update_cart_item_quantity(self):
        self.client.post(reverse("cart_add"), {"product_id": str(self.product.id), "quantity": 1})
        item = CartItem.objects.get(cart__user=self.user)
        response = self.client.patch(reverse("cart_item_update", args=[item.id]), {"quantity": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_remove_cart_item(self):
        self.client.post(reverse("cart_add"), {"product_id": str(self.product.id), "quantity": 1})
        item = CartItem.objects.get(cart__user=self.user)
        response = self.client.delete(reverse("cart_item_update", args=[item.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_save_for_later_excludes_from_active_items(self):
        self.client.post(reverse("cart_add"), {"product_id": str(self.product.id), "quantity": 1})
        item = CartItem.objects.get(cart__user=self.user)
        response = self.client.post(reverse("cart_save_for_later", args=[item.id]))
        self.assertEqual(len(response.data["items"]), 0)
        self.assertEqual(len(response.data["saved_items"]), 1)

    def test_apply_valid_coupon(self):
        Coupon.objects.create(
            code="SAVE10", discount_type="percent", discount_value=10,
            valid_until=timezone.now() + timedelta(days=7),
        )
        self.client.post(reverse("cart_add"), {"product_id": str(self.product.id), "quantity": 1})
        response = self.client.post(reverse("cart_apply_coupon"), {"code": "SAVE10"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["coupon_code"], "SAVE10")

    def test_apply_expired_coupon_fails(self):
        Coupon.objects.create(
            code="EXPIRED", discount_type="flat", discount_value=10,
            valid_until=timezone.now() - timedelta(days=1),
        )
        response = self.client.post(reverse("cart_apply_coupon"), {"code": "EXPIRED"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cart_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("cart_detail"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
