from django.db.models import Count, Avg
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import OrderItem
from products.models import Product
from products.serializers import ProductListSerializer
from .models import Review, ReviewHelpfulVote, ProductQuestion, ProductAnswer
from .serializers import ReviewSerializer, ReviewWriteSerializer, ProductQuestionSerializer, ProductAnswerSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Review.objects.select_related("user").prefetch_related("images")
        product_id = self.request.query_params.get("product")
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    def get_serializer_class(self):
        return ReviewWriteSerializer if self.action in ("create", "update", "partial_update") else ReviewSerializer

    def perform_create(self, serializer):
        product = serializer.validated_data["product"]
        is_verified = OrderItem.objects.filter(
            order__user=self.request.user, product=product, order__status="delivered"
        ).exists()
        review = serializer.save(user=self.request.user, is_verified_purchase=is_verified)
        self._recalculate_rating(product)

    def perform_update(self, serializer):
        review = serializer.save()
        self._recalculate_rating(review.product)

    def perform_destroy(self, instance):
        product = instance.product
        instance.delete()
        self._recalculate_rating(product)

    @staticmethod
    def _recalculate_rating(product):
        agg = Review.objects.filter(product=product).aggregate(avg=Avg("rating"), count=Count("id"))
        product.rating_avg = round(agg["avg"] or 0, 2)
        product.rating_count = agg["count"] or 0
        product.save(update_fields=["rating_avg", "rating_count"])

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def helpful(self, request, pk=None):
        review = self.get_object()
        _, created = ReviewHelpfulVote.objects.get_or_create(review=review, user=request.user)
        if created:
            review.helpful_count += 1
            review.save(update_fields=["helpful_count"])
        return Response({"helpful_count": review.helpful_count})


class ProductQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = ProductQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = ProductQuestion.objects.select_related("user").prefetch_related("answers")
        product_id = self.request.query_params.get("product")
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnswerQuestionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, question_id):
        question = ProductQuestion.objects.get(id=question_id)
        answer = ProductAnswer.objects.create(
            question=question,
            user=request.user,
            answer=request.data.get("answer", ""),
            is_seller_answer=request.user.is_staff,
        )
        return Response(ProductAnswerSerializer(answer).data, status=status.HTTP_201_CREATED)


class FrequentlyBoughtTogetherView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        order_ids = OrderItem.objects.filter(product_id=product_id).values_list("order_id", flat=True)
        co_purchased = (
            OrderItem.objects.filter(order_id__in=order_ids)
            .exclude(product_id=product_id)
            .values("product_id")
            .annotate(times_bought_together=Count("product_id"))
            .order_by("-times_bought_together")[:6]
        )
        product_ids = [row["product_id"] for row in co_purchased]
        products = Product.objects.filter(id__in=product_ids, is_active=True).prefetch_related("images")
        return Response(ProductListSerializer(products, many=True, context={"request": request}).data)
