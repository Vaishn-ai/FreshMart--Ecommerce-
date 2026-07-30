from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .seo import sitemap_view, robots_view

schema_view = get_schema_view(
    openapi.Info(title="FreshMart API", default_version="v1"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("sitemap.xml", sitemap_view, name="sitemap"),
    path("robots.txt", robots_view, name="robots"),

    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/", include("categories.urls")),
    path("api/v1/products/", include("products.urls")),
    path("api/v1/cart/", include("cart.urls")),
    path("api/v1/wishlist/", include("wishlist.urls")),
    path("api/v1/coupons/", include("coupons.urls")),
    path("api/v1/orders/", include("orders.urls")),
    path("api/v1/payments/", include("payments.urls")),
    path("api/v1/", include("reviews.urls")),
    path("api/v1/dashboard/", include("dashboard.urls")),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-docs"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
