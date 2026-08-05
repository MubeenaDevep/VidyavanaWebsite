import logging

from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminOrReadOnly

from .filters import CourseFilter
from .models import Course, CourseCategory
from .serializers import (
    CourseCategorySerializer,
    CourseDetailSerializer,
    CourseListSerializer,
)

logger = logging.getLogger("vidyavana")


class CourseCategoryViewSet(ModelViewSet):
    """CRUD for course categories. Public read, admin write."""

    serializer_class = CourseCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    filterset_fields = ["is_active"]
    search_fields = ["name", "tagline"]
    ordering_fields = ["order", "name", "created_at"]
    ordering = ["order"]

    def get_queryset(self):
        qs = CourseCategory.objects.all()
        if self.request.method == "GET" and not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs


class CourseViewSet(ModelViewSet):
    """
    list: All courses, filterable by category / level / fee range, searchable by name.
    retrieve: A single course by slug.
    create/update/delete: Admin only.
    """

    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    filterset_class = CourseFilter
    search_fields = ["name", "short_description", "description", "category__name"]
    ordering_fields = ["order", "name", "fee", "created_at"]
    ordering = ["order"]

    def get_queryset(self):
        qs = Course.objects.select_related("category").all()
        if self.request.method == "GET" and not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        return CourseDetailSerializer

    def perform_create(self, serializer):
        course = serializer.save()
        logger.info("Course created: %s (id=%s)", course.name, course.id)

    def perform_update(self, serializer):
        course = serializer.save()
        logger.info("Course updated: %s (id=%s)", course.name, course.id)
