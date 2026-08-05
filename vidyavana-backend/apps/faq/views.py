from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminOrReadOnly

from .models import FAQ, FAQCategory, FAQQuestion
from .serializers import (
    FAQCategorySerializer,
    FAQQuestionCreateSerializer,
    FAQQuestionSerializer,
    FAQSerializer,
)


class FAQCategoryViewSet(ModelViewSet):
    serializer_class = FAQCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["order", "name"]
    ordering = ["order"]

    def get_queryset(self):
        qs = FAQCategory.objects.all()
        if self.request.method == "GET" and not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs


class FAQViewSet(ModelViewSet):
    """Public read of active FAQs, admin manages full CRUD."""

    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["is_active", "category"]
    search_fields = ["question", "answer"]
    ordering_fields = ["order", "created_at"]
    ordering = ["order"]

    def get_queryset(self):
        qs = FAQ.objects.select_related("category").all()
        if self.request.method == "GET" and not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs


class FAQQuestionViewSet(ModelViewSet):
    """Public submission of FAQ questions, admin review via list/retrieve."""

    serializer_class = FAQQuestionSerializer
    filterset_fields = ["is_reviewed"]
    search_fields = ["name", "email", "question"]
    ordering_fields = ["created_at", "is_reviewed"]
    ordering = ["-created_at"]
    queryset = FAQQuestion.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == "create":
            return FAQQuestionCreateSerializer
        return FAQQuestionSerializer

    def perform_create(self, serializer):
        serializer.save()
