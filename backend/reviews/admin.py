from django.contrib import admin
from .models import Review, ReviewImage, ProductQuestion, ProductAnswer


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_verified_purchase", "helpful_count", "created_at")
    list_filter = ("rating", "is_verified_purchase")
    search_fields = ("product__name", "user__email")
    inlines = [ReviewImageInline]


class ProductAnswerInline(admin.TabularInline):
    model = ProductAnswer
    extra = 0


@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "question", "created_at")
    inlines = [ProductAnswerInline]
