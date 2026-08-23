from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from products.models import Product, ProductVariant
from coupons.models import Coupon, CouponUsage
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer
from coupons.serializers import ApplyCouponSerializer


class BaseCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    def cart_response(self, cart, status_code=status.HTTP_200_OK):
        """
        Serialize the cart with request context attached — required so nested
        product images (CartItemSerializer -> product_detail.primary_image)
        resolve to absolute URLs instead of bare relative paths.
        """
        return Response(CartSerializer(cart, context={"request": self.request}).data, status=status_code)


class CartDetailView(BaseCartView):
    def get(self, request):
        cart = self.get_cart(request)
        return self.cart_response(cart)


class AddToCartView(BaseCartView):
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        product = get_object_or_404(Product, id=data["product_id"], is_active=True)
        variant = None
        if data.get("variant_id"):
            variant = get_object_or_404(ProductVariant, id=data["variant_id"], product=product, is_active=True)

        available_stock = variant.stock if variant else product.stock
        cart = self.get_cart(request)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant,
            defaults={"quantity": data["quantity"]},
        )
        if not created:
            item.quantity += data["quantity"]

        if item.quantity > available_stock:
            return Response({"detail": "Not enough stock available."}, status=status.HTTP_400_BAD_REQUEST)

        item.saved_for_later = False
        item.save()
        return self.cart_response(cart, status.HTTP_201_CREATED)


class UpdateCartItemView(BaseCartView):
    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.get_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        available_stock = item.available_stock

        if serializer.validated_data["quantity"] > available_stock:
            return Response({"detail": "Not enough stock available."}, status=status.HTTP_400_BAD_REQUEST)

        item.quantity = serializer.validated_data["quantity"]
        item.save()
        return self.cart_response(cart)

    def delete(self, request, item_id):
        cart = self.get_cart(request)
        get_object_or_404(CartItem, id=item_id, cart=cart).delete()
        return self.cart_response(cart)


class SaveForLaterView(BaseCartView):
    def post(self, request, item_id):
        cart = self.get_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.saved_for_later = True
        item.save()
        return self.cart_response(cart)

    def delete(self, request, item_id):
        """Move a saved-for-later item back to the active cart."""
        cart = self.get_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        if item.quantity > item.available_stock:
            return Response({"detail": "Not enough stock to move back to cart."}, status=status.HTTP_400_BAD_REQUEST)
        item.saved_for_later = False
        item.save()
        return self.cart_response(cart)


class ApplyCouponView(BaseCartView):
    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"].strip().upper()

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({"detail": "Invalid coupon code."}, status=status.HTTP_400_BAD_REQUEST)

        if not coupon.is_valid_now():
            return Response({"detail": "This coupon has expired or is no longer active."}, status=status.HTTP_400_BAD_REQUEST)

        usage_count = CouponUsage.objects.filter(coupon=coupon, user=request.user).count()
        if usage_count >= coupon.usage_limit_per_user:
            return Response({"detail": "You've already used this coupon the maximum number of times."}, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_cart(request)
        if cart.subtotal < coupon.min_order_value:
            return Response(
                {"detail": f"Minimum order value for this coupon is ₹{coupon.min_order_value}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart.coupon = coupon
        cart.save()
        return self.cart_response(cart)

    def delete(self, request):
        cart = self.get_cart(request)
        cart.coupon = None
        cart.save()
        return self.cart_response(cart)


class ClearCartView(BaseCartView):
    def delete(self, request):
        cart = self.get_cart(request)
        cart.items.filter(saved_for_later=False).delete()
        return self.cart_response(cart)
