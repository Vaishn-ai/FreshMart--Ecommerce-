import uuid
from django.db import models
from django.utils.text import slugify
from categories.models import Category, Brand


class Product(models.Model):
    UNIT_CHOICES = (("kg", "Kg"), ("g", "Gram"), ("l", "Litre"), ("ml", "ml"), ("pcs", "Pieces"), ("pack", "Pack"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, related_name="products", null=True, blank=True, on_delete=models.SET_NULL)

    description = models.TextField(blank=True)
    highlights = models.JSONField(default=list, blank=True)          # ["Highlight 1", "Highlight 2"]
    specifications = models.JSONField(default=dict, blank=True)      # {"Origin": "India", ...}
    nutrition_facts = models.JSONField(default=dict, blank=True)     # {"Calories": "52 kcal", ...}

    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="pcs")
    weight_or_size = models.CharField(max_length=50, blank=True)     # e.g. "500g", "1L", "XL"
    color = models.CharField(max_length=50, blank=True)

    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=64, unique=True)
    barcode = models.CharField(max_length=64, blank=True)

    is_featured = models.BooleanField(default=False)
    is_flash_sale = models.BooleanField(default=False)
    flash_sale_ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)  # drives "best sellers"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_featured"]),
            models.Index(fields=["is_flash_sale"]),
            models.Index(fields=["-sold_count"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            self.slug = f"{base}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

    @property
    def discount_percent(self):
        if self.mrp and self.mrp > 0:
            return round((1 - (self.discount_price / self.mrp)) * 100)
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=150, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """E.g. same product in different weights/sizes/colors, each with its own price & stock."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)          # e.g. "1kg", "Red / XL"
    sku = models.CharField(max_length=64, unique=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} — {self.name}"


class RecentlyViewed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("accounts.User", related_name="recently_viewed", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-viewed_at"]


class SearchLog(models.Model):
    """Powers 'recent searches' for logged-in users and lets admins see trending queries."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("accounts.User", null=True, blank=True, related_name="search_logs", on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    result_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
