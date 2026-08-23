from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, Address


class RegistrationLoginTests(APITestCase):
    def test_register_creates_user_and_returns_tokens(self):
        url = reverse("register")
        payload = {
            "username": "janedoe",
            "email": "jane@example.com",
            "phone": "9999999999",
            "password": "StrongPass123",
            "password2": "StrongPass123",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(User.objects.filter(email="jane@example.com").exists())

    def test_register_rejects_mismatched_passwords(self):
        url = reverse("register")
        payload = {
            "username": "janedoe",
            "email": "jane@example.com",
            "password": "StrongPass123",
            "password2": "DifferentPass456",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_valid_credentials(self):
        User.objects.create_user(username="janedoe", email="jane@example.com", password="StrongPass123")
        url = reverse("login")
        response = self.client.post(url, {"email": "jane@example.com", "password": "StrongPass123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_with_invalid_credentials(self):
        User.objects.create_user(username="janedoe", email="jane@example.com", password="StrongPass123")
        url = reverse("login")
        response = self.client.post(url, {"email": "jane@example.com", "password": "wrong"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileAndAddressTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="janedoe", email="jane@example.com", password="StrongPass123")
        self.client.force_authenticate(user=self.user)

    def test_get_profile_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_own_profile(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "jane@example.com")

    def test_create_address(self):
        url = reverse("address-list")
        payload = {
            "label": "home", "full_name": "Jane Doe", "phone": "9999999999",
            "line1": "123 Main St", "city": "Nagpur", "state": "Maharashtra", "pincode": "440001",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.filter(user=self.user).count(), 1)

    def test_only_one_default_address(self):
        Address.objects.create(user=self.user, full_name="A", phone="1", line1="x", city="c", state="s", pincode="1", is_default=True)
        Address.objects.create(user=self.user, full_name="B", phone="2", line1="y", city="c", state="s", pincode="2", is_default=True)
        self.assertEqual(Address.objects.filter(user=self.user, is_default=True).count(), 1)
