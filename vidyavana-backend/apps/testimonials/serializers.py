from rest_framework import serializers

from .models import Testimonial


class TestimonialSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True, default=None)

    class Meta:
        model = Testimonial
        fields = [
            "id",
            "uuid",
            "name",
            "role_or_course",
            "course",
            "course_name",
            "photo",
            "quote",
            "rating",
            "is_featured",
            "is_active",
            "order",
            "created_at",
        ]
        read_only_fields = ["id", "uuid", "created_at"]

    def validate_quote(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Quote must be at least 10 characters.")
        return value
