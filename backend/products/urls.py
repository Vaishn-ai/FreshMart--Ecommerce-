from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, RecentSearchesView, TrendingSearchesView, VoiceSearchView

router = DefaultRouter()
router.register("", ProductViewSet, basename="product")

urlpatterns = [
    path("search/recent/", RecentSearchesView.as_view(), name="recent_searches"),
    path("search/trending/", TrendingSearchesView.as_view(), name="trending_searches"),
    path("search/voice/", VoiceSearchView.as_view(), name="voice_search"),
    path("", include(router.urls)),
]
