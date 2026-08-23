import uuid
from django.db import models
from django.utils import timezone
from accounts.models import Address
from products.models import Product, ProductVariant
from coupons.models import Coupon


def generate_order_number():
    return f"FM{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("returned", "Returned"),
    )
    PAYMENT_METHODS = (("cod", "Cash on Delivery"), ("stripe", "Stripe"), ("razorpay", "Razorpay"), ("upi", "UPI"))
    PAYMENT_STATUS = (("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed"), ("refunded", "Refunded"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=32, unique=True, default=generate_order_number, editable=False)
    user = models.ForeignKey("accounts.User", related_name="orders", on_delete=models.PROTECT)

    # Address snapshot (so later address edits don't rewrite past orders)
    shipping_name = models.CharField(max_length=150)
    shipping_phone = models.CharField(max_length=20)
    shipping_line1 = models.CharField(max_length=255)
    shipping_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=12)
    shipping_country = models.CharField(max_length=100, default="India")

    shipping_method = models.CharField(max_length=20, default="standard")  # standard / express
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default="pending")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")

    tracking_number = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status"]), models.Index(fields=["user", "-created_at"])]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)

    # Snapshots at time of purchase
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"


class OrderStatusHistory(models.Model):
    """Timeline of status changes for order tracking."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name="status_history", on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=Order.STATUS_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["changed_at"]
