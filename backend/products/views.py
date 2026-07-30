from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, RecentlyViewed, SearchLog
from .filters import ProductFilter
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductWriteSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    list/retrieve are public; write actions require IsAdminUser.
    Extra actions cover featured / flash-sale / best-sellers / trending / recommended / recently-viewed.
    """
    queryset = Product.objects.filter(is_active=True).select_related("category", "brand").prefetch_related("images", "variants")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["discount_price", "rating_avg", "created_at", "sold_count"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        if self.action in ("create", "update", "partial_update"):
            return ProductWriteSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_authenticated:
            RecentlyViewed.objects.update_or_create(user=request.user, product=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        query = request.query_params.get("search")
        if query:
            count = response.data.get("count", len(response.data)) if isinstance(response.data, dict) else len(response.data)
            SearchLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                query=query,
                result_count=count,
            )
        return response

    @action(detail=False)
    def autocomplete(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 2:
            return Response([])
        names = (
            self.get_queryset()
            .filter(name__icontains=query)
            .values_list("name", flat=True)
            .distinct()[:8]
        )
        return Response(list(names))

    @action(detail=False, url_path="compare")
    def compare(self, request):
        ids = request.query_params.get("ids", "")
        product_ids = [pid for pid in ids.split(",") if pid][:4]
        if not product_ids:
            return Response({"detail": "Provide up to 4 product ids via ?ids=a,b,c"}, status=status.HTTP_400_BAD_REQUEST)
        products = self.get_queryset().filter(id__in=product_ids)
        serializer = ProductDetailSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)


    @action(detail=False)
    @method_decorator(cache_page(60))
    def featured(self, request):
        qs = self.filter_queryset(self.get_queryset().filter(is_featured=True))
        return self._paginated(qs)

    @action(detail=False, url_path="flash-sale")
    def flash_sale(self, request):
        qs = self.filter_queryset(
            self.get_queryset().filter(is_flash_sale=True, flash_sale_ends_at__gt=timezone.now())
        )
        return self._paginated(qs)

    @action(detail=False, url_path="best-sellers")
    def best_sellers(self, request):
        qs = self.filter_queryset(self.get_queryset().order_by("-sold_count"))
        return self._paginated(qs)

    @action(detail=False)
    def trending(self, request):
        # Proxy for "trending": highest rated with recent activity. Swap in real analytics later.
        qs = self.filter_queryset(self.get_queryset().order_by("-rating_avg", "-sold_count"))
        return self._paginated(qs)

    @action(detail=False)
    def recommended(self, request):
        if not request.user.is_authenticated:
            qs = self.get_queryset().order_by("-rating_avg")[:20]
        else:
            viewed_categories = RecentlyViewed.objects.filter(user=request.user).values_list("product__category_id", flat=True)
            qs = self.get_queryset().filter(category_id__in=viewed_categories).order_by("-rating_avg")
        return self._paginated(qs)

    @action(detail=False, url_path="recently-viewed", permission_classes=[permissions.IsAuthenticated])
    def recently_viewed(self, request):
        product_ids = RecentlyViewed.objects.filter(user=request.user).order_by("-viewed_at").values_list("product_id", flat=True)[:20]
        products = list(self.get_queryset().filter(id__in=product_ids))
        products.sort(key=lambda p: list(product_ids).index(p.id))
        serializer = ProductListSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)

    def _paginated(self, qs):
        page = self.paginate_queryset(qs)
        serializer = ProductListSerializer(page or qs, many=True, context={"request": self.request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class RecentSearchesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queries = (
            SearchLog.objects.filter(user=request.user)
            .order_by("-created_at")
            .values_list("query", flat=True)
            .distinct()[:10]
        )
        return Response(list(queries))

    def delete(self, request):
        SearchLog.objects.filter(user=request.user).delete()
        return Response(status=204)


class TrendingSearchesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        since = timezone.now() - timezone.timedelta(days=7)
        trending = (
            SearchLog.objects.filter(created_at__gte=since)
            .values("query")
            .annotate(count=Count("query"))
            .order_by("-count")[:10]
        )
        return Response(list(trending))


class VoiceSearchView(APIView):
    """
    Accepts already-transcribed text from the browser's Web Speech API (frontend does the
    speech-to-text) and runs it through the normal product search — kept as a separate,
    documented endpoint so the frontend has a clear contract for the mic button.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        transcript = request.data.get("transcript", "").strip()
        if not transcript:
            return Response({"detail": "No transcript provided."}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.filter(is_active=True, name__icontains=transcript).prefetch_related("images")[:20]
        SearchLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query=transcript,
            result_count=products.count(),
        )
        return Response({
            "transcript": transcript,
            "results": ProductListSerializer(products, many=True, context={"request": request}).data,
        })
