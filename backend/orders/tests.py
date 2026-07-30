from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User, Address
from categories.models import Category
from products.models import Product
from cart.models import Cart, CartItem
from .models import Order
from .services import create_order_from_cart, CheckoutError


class CheckoutServiceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", email="buyer@example.com", password="StrongPass123")
        category = Category.objects.create(name="Dairy")
        self.product = Product.objects.create(
            name="Milk 1L", category=category, mrp=Decimal("60.00"),
            discount_price=Decimal("55.00"), stock=20, sku="MILK-1",
        )
        self.address = Address.objects.create(
            user=self.user, full_name="Buyer One", phone="9999999999",
            line1="12 Market Rd", city="Nagpur", state="Maharashtra", pincode="440001",
        )
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_checkout_creates_order_and_clears_cart(self):
        order = create_order_from_cart(self.user, self.address.id, "standard", "cod")
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.status, "confirmed")  # COD auto-confirms
        self.assertEqual(order.payment_status, "paid")
        self.assertEqual(self.cart.items.filter(saved_for_later=False).count(), 0)

    def test_checkout_decrements_stock(self):
        create_order_from_cart(self.user, self.address.id, "standard", "cod")
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 18)

    def test_checkout_with_empty_cart_raises(self):
        self.cart.items.all().delete()
        with self.assertRaises(CheckoutError):
            create_order_from_cart(self.user, self.address.id, "standard", "cod")

    def test_online_payment_leaves_order_pending(self):
        order = create_order_from_cart(self.user, self.address.id, "standard", "razorpay")
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.payment_status, "pending")

    def test_express_shipping_adds_surcharge(self):
        order = create_order_from_cart(self.user, self.address.id, "express", "cod")
        self.assertGreaterEqual(order.delivery_charge, Decimal("49.00"))


class OrderAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", email="buyer@example.com", password="StrongPass123")
        self.client.force_authenticate(user=self.user)
        category = Category.objects.create(name="Dairy")
        self.product = Product.objects.create(
            name="Milk 1L", category=category, mrp=Decimal("60.00"),
            discount_price=Decimal("55.00"), stock=20, sku="MILK-2",
        )
        self.address = Address.objects.create(
            user=self.user, full_name="Buyer One", phone="9999999999",
            line1="12 Market Rd", city="Nagpur", state="Maharashtra", pincode="440001",
        )
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

    def test_checkout_endpoint(self):
        response = self.client.post(reverse("checkout"), {
            "address_id": str(self.address.id), "shipping_method": "standard", "payment_method": "cod",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(user=self.user).exists())

    def test_list_own_orders_only(self):
        other_user = User.objects.create_user(username="other", email="other@example.com", password="x")
        Order.objects.create(
            user=other_user, shipping_name="X", shipping_phone="0", shipping_line1="x",
            shipping_city="c", shipping_state="s", shipping_pincode="1",
            subtotal=10, total=10, payment_method="cod",
        )
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.data["count"], 0)

    def test_cancel_pending_order(self):
        order = Order.objects.create(
            user=self.user, shipping_name="X", shipping_phone="0", shipping_line1="x",
            shipping_city="c", shipping_state="s", shipping_pincode="1",
            subtotal=10, total=10, payment_method="cod", status="pending",
        )
        response = self.client.post(reverse("order-cancel", args=[order.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")

    def test_cannot_cancel_delivered_order(self):
        order = Order.objects.create(
            user=self.user, shipping_name="X", shipping_phone="0", shipping_line1="x",
            shipping_city="c", shipping_state="s", shipping_pincode="1",
            subtotal=10, total=10, payment_method="cod", status="delivered",
        )
        response = self.client.post(reverse("order-cancel", args=[order.id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
