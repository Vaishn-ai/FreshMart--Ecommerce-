import uuid
from django.db import models
from orders.models import Order


class Payment(models.Model):
    STATUS_CHOICES = (("created", "Created"), ("succeeded", "Succeeded"), ("failed", "Failed"), ("refunded", "Refunded"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, related_name="payment", on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=Order.PAYMENT_METHODS)
    provider_order_id = models.CharField(max_length=128, blank=True)   # Razorpay order_id / Stripe PaymentIntent id
    provider_payment_id = models.CharField(max_length=128, blank=True)
    provider_signature = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default="INR")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="created")
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider} — {self.order.order_number} — {self.status}"
