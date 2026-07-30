from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from categories.models import Category
from .models import Product


def make_product(**kwargs):
    category = kwargs.pop("category", None) or Category.objects.create(name="Vegetables")
    defaults = dict(
        name="Organic Tomatoes", category=category, mrp=Decimal("50.00"),
        discount_price=Decimal("40.00"), stock=25, sku=f"SKU-{Product.objects.count()+1}",
    )
    defaults.update(kwargs)
    return Product.objects.create(**defaults)


class ProductListTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fruits")
        make_product(name="Apples", category=self.category, is_featured=True)
        make_product(name="Bananas", category=self.category)
        make_product(name="Milk", category=self.category, stock=0)

    def test_list_products(self):
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_filter_by_category_slug(self):
        response = self.client.get(reverse("product-list"), {"category": self.category.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_filter_in_stock(self):
        response = self.client.get(reverse("product-list"), {"in_stock": "true"})
        self.assertEqual(response.data["count"], 2)

    def test_featured_endpoint(self):
        response = self.client.get(reverse("product-featured"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p["name"] for p in response.data["results"]]
        self.assertIn("Apples", names)

    def test_search_products(self):
        response = self.client.get(reverse("product-list"), {"search": "Apples"})
        self.assertEqual(response.data["count"], 1)

    def test_discount_percent_calculation(self):
        product = make_product(name="Discounted Item", mrp=Decimal("100.00"), discount_price=Decimal("75.00"))
        self.assertEqual(product.discount_percent, 25)


class ProductDetailTests(APITestCase):
    def test_retrieve_product_by_id(self):
        product = make_product()
        response = self.client.get(reverse("product-detail", args=[product.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], product.name)

    def test_only_admin_can_create_product(self):
        category = Category.objects.create(name="Bakery")
        payload = {
            "name": "Bread", "category": str(category.id), "mrp": "60.00",
            "discount_price": "50.00", "stock": 10, "sku": "BREAD-1",
        }
        response = self.client.post(reverse("product-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
