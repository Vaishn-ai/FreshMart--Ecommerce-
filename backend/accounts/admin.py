from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "phone", "is_email_verified", "is_staff", "created_at")
    search_fields = ("email", "username", "phone")
    ordering = ("-created_at",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Extra", {"fields": ("phone", "profile_image", "is_email_verified", "google_id")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "label", "city", "state", "is_default")
    list_filter = ("label", "is_default")
    search_fields = ("user__email", "city", "pincode")
