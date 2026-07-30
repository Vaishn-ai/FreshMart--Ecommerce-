from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("reviews", views.ReviewViewSet, basename="review")
router.register("questions", views.ProductQuestionViewSet, basename="question")

urlpatterns = [
    path("questions/<uuid:question_id>/answer/", views.AnswerQuestionView.as_view(), name="answer_question"),
    path("products/<uuid:product_id>/frequently-bought-together/", views.FrequentlyBoughtTogetherView.as_view(), name="fbt"),
    path("", include(router.urls)),
]
