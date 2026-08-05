from rest_framework import serializers

from .models import FAQ, FAQCategory, FAQQuestion


class FAQCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQCategory
        fields = ["id", "name", "is_active", "order"]
        read_only_fields = ["id"]


class FAQSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)

    class Meta:
        model = FAQ
        fields = [
            "id",
            "category",
            "category_name",
            "question",
            "answer",
            "is_active",
            "order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_question(self, value):
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError("Question must be at least 5 characters.")
        return value

    def validate_answer(self, value):
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError("Answer must be at least 5 characters.")
        return value


class FAQQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQQuestion
        fields = ["id", "uuid", "name", "email", "question", "is_reviewed", "created_at"]
        read_only_fields = ["id", "uuid", "is_reviewed", "created_at"]

    def validate_question(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Question must be at least 10 characters.")
        return value


class FAQQuestionCreateSerializer(FAQQuestionSerializer):
    class Meta(FAQQuestionSerializer.Meta):
        fields = ["id", "name", "email", "question"]
        extra_kwargs = {"email": {"write_only": True}}
