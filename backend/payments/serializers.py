from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "order", "provider", "provider_order_id", "amount", "currency", "status", "created_at"]
        read_only_fields = fields


class RazorpayVerifySerializer(serializers.Serializer):
    order_id = serializers.UUIDField()          # our internal Order id
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()


class StripeConfirmSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    payment_intent_id = serializers.CharField()


class UpiInitiateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    upi_id = serializers.CharField()
