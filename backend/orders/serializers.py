from rest_framework import serializers
from accounts.models import Address
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.ReadOnlyField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "variant", "product_name", "unit_price", "quantity", "line_total", "product_image"]

    def get_product_image(self, obj):
        img = obj.product.images.filter(is_primary=True).first() or obj.product.images.first()
        if not img or not img.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(img.image.url) if request else img.image.url


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ["status", "note", "changed_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "shipping_name", "shipping_phone", "shipping_line1", "shipping_line2",
            "shipping_city", "shipping_state", "shipping_pincode", "shipping_country", "shipping_method",
            "subtotal", "discount_amount", "delivery_charge", "tax_amount", "total",
            "payment_method", "payment_status", "status", "tracking_number", "notes",
            "items", "status_history", "created_at",
        ]
        read_only_fields = fields


class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.UUIDField()
    shipping_method = serializers.ChoiceField(choices=["standard", "express"], default="standard")
    payment_method = serializers.ChoiceField(choices=["cod", "stripe", "razorpay", "upi"])

    def validate_address_id(self, value):
        request = self.context["request"]
        if not Address.objects.filter(id=value, user=request.user).exists():
            raise serializers.ValidationError("Address not found.")
        return value
