from rest_framework import serializers
from .models import Review, ReviewImage, ProductQuestion, ProductAnswer


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ["id", "image"]


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "product", "user_name", "rating", "title", "comment",
            "is_verified_purchase", "helpful_count", "images", "created_at",
        ]
        read_only_fields = ["id", "user_name", "is_verified_purchase", "helpful_count", "created_at"]


class ReviewWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["product", "rating", "title", "comment"]

    def validate_product(self, product):
        request = self.context["request"]
        if Review.objects.filter(product=product, user=request.user).exists() and self.instance is None:
            raise serializers.ValidationError("You've already reviewed this product.")
        return product


class ProductAnswerSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ProductAnswer
        fields = ["id", "question", "user_name", "answer", "is_seller_answer", "helpful_count", "created_at"]
        read_only_fields = ["id", "user_name", "is_seller_answer", "helpful_count", "created_at"]


class ProductQuestionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    answers = ProductAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = ProductQuestion
        fields = ["id", "product", "user_name", "question", "answers", "created_at"]
        read_only_fields = ["id", "user_name", "answers", "created_at"]
