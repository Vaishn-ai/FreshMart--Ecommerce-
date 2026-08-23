import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", related_name="reviews", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=150, blank=True)
    comment = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-helpful_count", "-created_at"]

    def __str__(self):
        return f"{self.product.name} — {self.rating}★ by {self.user.email}"


class ReviewImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="reviews/")


class ReviewHelpfulVote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, related_name="votes", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "user")


class ProductQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, related_name="questions", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", related_name="questions", on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ProductAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(ProductQuestion, related_name="answers", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", related_name="answers", on_delete=models.CASCADE)
    answer = models.CharField(max_length=1000)
    is_seller_answer = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_seller_answer", "-helpful_count", "-created_at"]
