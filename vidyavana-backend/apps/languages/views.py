from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminOrReadOnly

from .models import Language
from .serializers import LanguageSerializer


class LanguageViewSet(ModelViewSet):
    """
    list: All active languages, ordered for display in nav / chatbot switchers.
    retrieve: A single language by id.
    create/update/delete: Admin only.
    """

    serializer_class = LanguageSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["is_active", "is_default"]
    search_fields = ["code", "name", "native_name"]
    ordering_fields = ["order", "name", "created_at"]
    ordering = ["order"]

    def get_queryset(self):
        qs = Language.objects.all()
        if self.request.method == "GET" and not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs
