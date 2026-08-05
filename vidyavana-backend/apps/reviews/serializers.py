from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True, default=None)

    class Meta:
        model = Review
        fields = [
            "id",
            "uuid",
            "name",
            "course",
            "course_name",
            "rating",
            "title",
            "message",
            "is_approved",
            "created_at",
        ]
        read_only_fields = ["id", "uuid", "is_approved", "created_at"]

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Review message must be at least 10 characters.")
        return value

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ReviewCreateSerializer(ReviewSerializer):
    class Meta(ReviewSerializer.Meta):
        fields = ["id", "name", "email", "course", "rating", "title", "message"]
        extra_kwargs = {"email": {"write_only": True}}
