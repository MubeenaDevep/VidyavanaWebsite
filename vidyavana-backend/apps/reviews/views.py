import logging

from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.throttling import AnonRateThrottle

from .models import Review
from .serializers import ReviewCreateSerializer, ReviewSerializer

logger = logging.getLogger("vidyavana")


class ReviewThrottle(AnonRateThrottle):
    scope = "contact"  # reuse the conservative 'contact' rate for public submissions


class ReviewViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    list/retrieve: Publicly visible, approved reviews only.
    create: Public submission (goes to a pending-approval queue).
    destroy: Admin only.
    Admins can see all reviews (approved + pending) via ?all=true.
    """

    filterset_fields = ["rating", "course", "is_approved"]
    search_fields = ["name", "title", "message"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Review.objects.select_related("course").all()
        if self.request.user.is_staff and self.request.query_params.get("all") == "true":
            return qs
        return qs.filter(is_approved=True)

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]
        return [AllowAny()]

    def get_throttles(self):
        if self.action == "create":
            return [ReviewThrottle()]
        return super().get_throttles()

    def perform_create(self, serializer):
        review = serializer.save()
        logger.info("New review submitted by %s (id=%s), pending approval", review.name, review.id)
