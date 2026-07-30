from rest_framework import serializers
from products.serializers import ProductListSerializer, ProductVariantSerializer
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source="product", read_only=True)
    variant_detail = ProductVariantSerializer(source="variant", read_only=True)
    unit_price = serializers.ReadOnlyField()
    line_total = serializers.ReadOnlyField()
    available_stock = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = [
            "id", "product", "product_detail", "variant", "variant_detail",
            "quantity", "saved_for_later", "unit_price", "line_total", "available_stock",
        ]
        read_only_fields = ["id"]


class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    saved_items = serializers.SerializerMethodField()
    subtotal = serializers.ReadOnlyField()
    discount_amount = serializers.ReadOnlyField()
    delivery_charge = serializers.ReadOnlyField()
    tax_amount = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    coupon_code = serializers.CharField(source="coupon.code", read_only=True, default=None)

    class Meta:
        model = Cart
        fields = [
            "id", "items", "saved_items", "coupon_code", "subtotal",
            "discount_amount", "delivery_charge", "tax_amount", "total", "updated_at",
        ]

    def get_items(self, obj):
        return CartItemSerializer(obj.items.filter(saved_for_later=False), many=True, context=self.context).data

    def get_saved_items(self, obj):
        return CartItemSerializer(obj.items.filter(saved_for_later=True), many=True, context=self.context).data


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
