from rest_framework import serializers
from categories.serializers import CategorySerializer, BrandSerializer
from .models import Product, ProductImage, ProductVariant


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_primary", "order"]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "name", "sku", "mrp", "discount_price", "stock", "is_active"]


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight — used for grids/listings."""
    primary_image = serializers.SerializerMethodField()
    discount_percent = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "unit", "weight_or_size", "mrp", "discount_price",
            "discount_percent", "in_stock", "rating_avg", "rating_count",
            "is_featured", "is_flash_sale", "primary_image",
        ]

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if not img or not img.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(img.image.url) if request else img.image.url


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    discount_percent = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "category", "brand", "description", "highlights",
            "specifications", "nutrition_facts", "unit", "weight_or_size", "color",
            "mrp", "discount_price", "discount_percent", "stock", "in_stock", "sku",
            "barcode", "is_featured", "is_flash_sale", "flash_sale_ends_at",
            "rating_avg", "rating_count", "sold_count", "images", "variants", "created_at",
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    """Used by admin dashboard for create/update."""
    class Meta:
        model = Product
        fields = [
            "name", "category", "brand", "description", "highlights", "specifications",
            "nutrition_facts", "unit", "weight_or_size", "color", "mrp", "discount_price",
            "stock", "sku", "barcode", "is_featured", "is_flash_sale", "flash_sale_ends_at", "is_active",
        ]

    def validate(self, attrs):
        if attrs.get("discount_price") and attrs.get("mrp") and attrs["discount_price"] > attrs["mrp"]:
            raise serializers.ValidationError("Discount price cannot exceed MRP.")
        return attrs
