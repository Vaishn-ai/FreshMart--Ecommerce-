from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from orders.models import Order
from orders.services import send_order_confirmation_email, advance_order_status
from .models import Payment
from .serializers import RazorpayVerifySerializer, StripeConfirmSerializer, UpiInitiateSerializer
from . import services


class RazorpayCreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user, payment_method="razorpay")
        try:
            rp_order = services.create_razorpay_order(order)
        except services.PaymentConfigError as e:
            return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        payment, _ = Payment.objects.update_or_create(
            order=order,
            defaults={"provider": "razorpay", "provider_order_id": rp_order["id"], "amount": order.total, "status": "created"},
        )
        return Response({
            "razorpay_order_id": rp_order["id"],
            "amount": rp_order["amount"],
            "currency": rp_order["currency"],
            "key_id_public": "set on frontend via VITE_RAZORPAY_KEY_ID",
        })


class RazorpayVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RazorpayVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        order = get_object_or_404(Order, id=data["order_id"], user=request.user)
        try:
            services.verify_razorpay_payment(
                data["razorpay_order_id"], data["razorpay_payment_id"], data["razorpay_signature"]
            )
        except services.PaymentConfigError as e:
            return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception:
            return Response({"detail": "Payment signature verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(Payment, order=order)
        payment.provider_payment_id = data["razorpay_payment_id"]
        payment.provider_signature = data["razorpay_signature"]
        payment.status = "succeeded"
        payment.save()

        order.payment_status = "paid"
        order.save(update_fields=["payment_status"])
        advance_order_status(order, "confirmed", note="Payment verified via Razorpay")
        send_order_confirmation_email(order)

        return Response({"detail": "Payment verified.", "order_status": order.status})


class StripeCreateIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user, payment_method="stripe")
        try:
            intent = services.create_stripe_payment_intent(order)
        except services.PaymentConfigError as e:
            return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        Payment.objects.update_or_create(
            order=order,
            defaults={"provider": "stripe", "provider_order_id": intent["id"], "amount": order.total, "status": "created"},
        )
        return Response({"client_secret": intent["client_secret"]})


class StripeConfirmView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = StripeConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        order = get_object_or_404(Order, id=data["order_id"], user=request.user)
        try:
            intent = services.retrieve_stripe_payment_intent(data["payment_intent_id"])
        except services.PaymentConfigError as e:
            return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if intent["status"] != "succeeded":
            return Response({"detail": f"Payment not completed (status: {intent['status']})."}, status=400)

        payment = get_object_or_404(Payment, order=order)
        payment.provider_payment_id = intent["id"]
        payment.status = "succeeded"
        payment.raw_response = {"status": intent["status"]}
        payment.save()

        order.payment_status = "paid"
        order.save(update_fields=["payment_status"])
        advance_order_status(order, "confirmed", note="Payment confirmed via Stripe")
        send_order_confirmation_email(order)

        return Response({"detail": "Payment confirmed.", "order_status": order.status})


class UpiInitiateView(APIView):
    """
    Simplified UPI flow: generates a UPI deep link / QR payload. Real settlement confirmation
    would arrive via a bank/PSP webhook in production — wire that into StripeConfirmView-style
    logic once a UPI PSP (e.g. Razorpay UPI, Cashfree) is selected.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UpiInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        order = get_object_or_404(Order, id=data["order_id"], user=request.user, payment_method="upi")

        Payment.objects.update_or_create(
            order=order,
            defaults={"provider": "upi", "amount": order.total, "status": "created", "raw_response": {"upi_id": data["upi_id"]}},
        )
        upi_link = f"upi://pay?pa={data['upi_id']}&pn=FreshMart&am={order.total}&cu=INR&tn={order.order_number}"
        return Response({"upi_link": upi_link, "detail": "Complete payment in your UPI app, then poll order status."})
