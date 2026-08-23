from rest_framework import viewsets, permissions
from .models import Coupon
from .serializers import CouponSerializer


class CouponViewSet(viewsets.ModelViewSet):
    """Admin-managed. Public users never list all coupons directly — they apply by code via the cart app."""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
