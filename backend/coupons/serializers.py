from rest_framework import serializers
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id", "code", "description", "discount_type", "discount_value",
            "max_discount_amount", "min_order_value", "valid_from", "valid_until", "is_active",
        ]


class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField()
