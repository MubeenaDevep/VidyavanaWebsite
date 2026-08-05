from rest_framework import serializers

from .models import Course, CourseCategory


class CourseCategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseCategory
        fields = [
            "id",
            "name",
            "slug",
            "tagline",
            "icon",
            "is_active",
            "order",
            "course_count",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "created_at"]

    def get_course_count(self, obj):
        return obj.courses.filter(is_active=True).count()


class CourseListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "uuid",
            "name",
            "slug",
            "short_description",
            "duration",
            "level",
            "fee",
            "image",
            "category",
            "category_slug",
            "certificate_included",
            "is_featured",
            "is_active",
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    category = CourseCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=CourseCategory.objects.all(), write_only=True
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "uuid",
            "name",
            "slug",
            "short_description",
            "description",
            "duration",
            "level",
            "fee",
            "image",
            "category",
            "category_id",
            "certificate_included",
            "is_featured",
            "is_active",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "slug", "created_at", "updated_at"]

    def validate_fee(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Fee cannot be negative.")
        return value

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Course name must be at least 3 characters.")
        return value
