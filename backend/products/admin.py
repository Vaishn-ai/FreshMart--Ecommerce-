from django.contrib import admin
from .models import Product, ProductImage, ProductVariant, RecentlyViewed


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "discount_price", "mrp", "stock", "is_featured", "is_flash_sale", "is_active")
    list_filter = ("is_active", "is_featured", "is_flash_sale", "category")
    search_fields = ("name", "sku", "barcode")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductVariantInline]


admin.site.register(RecentlyViewed)


from .models import SearchLog


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("query", "user", "result_count", "created_at")
    search_fields = ("query",)
