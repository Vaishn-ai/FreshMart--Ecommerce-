import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product, ProductVariant
from coupons.models import Coupon


class Cart(models.Model):
    """One active cart per user."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField("accounts.User", related_name="cart", on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def items_active(self):
        return self.items.filter(saved_for_later=False)

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items_active), Decimal("0.00"))

    @property
    def discount_amount(self):
        if self.coupon and self.coupon.is_valid_now():
            return self.coupon.calculate_discount(self.subtotal)
        return Decimal("0.00")

    @property
    def delivery_charge(self):
        # Free delivery above ₹499, flat ₹40 otherwise. Configurable later via settings/admin.
        subtotal_after_discount = self.subtotal - self.discount_amount
        if subtotal_after_discount >= Decimal("499.00") or subtotal_after_discount <= 0:
            return Decimal("0.00")
        return Decimal("40.00")

    @property
    def tax_amount(self):
        # 5% GST on (subtotal - discount), typical for grocery essentials in India. Adjust per category later.
        taxable = max(self.subtotal - self.discount_amount, Decimal("0.00"))
        return (taxable * Decimal("0.05")).quantize(Decimal("0.01"))

    @property
    def total(self):
        return (self.subtotal - self.discount_amount + self.delivery_charge + self.tax_amount).quantize(Decimal("0.01"))

    def __str__(self):
        return f"Cart({self.user.email})"


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    saved_for_later = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product", "variant")

    @property
    def unit_price(self):
        return self.variant.discount_price if self.variant else self.product.discount_price

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    @property
    def available_stock(self):
        return self.variant.stock if self.variant else self.product.stock

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
