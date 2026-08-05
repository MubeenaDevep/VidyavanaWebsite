from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminOrReadOnly

from .models import Testimonial
from .serializers import TestimonialSerializer


class TestimonialViewSet(ModelViewSet):
    """Public read of active/featured testimonials; admin manages full CRUD."""

    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["is_featured", "is_active", "course"]
    search_fields = ["name", "role_or_course", "quote"]
    ordering_fields = ["order", "created_at", "rating"]
    ordering = ["order"]

    def get_queryset(self):
        qs = Testimonial.objects.select_related("course").all()
        if self.request.method == "GET" and not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs
