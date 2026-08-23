from django.contrib import admin
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "times_used", "usage_limit_total", "is_active", "valid_until")
    list_filter = ("is_active", "discount_type")
    search_fields = ("code",)


admin.site.register(CouponUsage)
