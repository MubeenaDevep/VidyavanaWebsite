import logging

from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.throttling import AnonRateThrottle

from apps.notifications.views import push_notification

from .filters import EnquiryFilter
from .models import Enquiry
from .serializers import EnquirySerializer

logger = logging.getLogger("vidyavana")


class EnquiryThrottle(AnonRateThrottle):
    scope = "enquiry"


class EnquiryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    create: Public — 'Enroll Now' / course-interest form.
    list/retrieve/update: Admin only — the placement/admissions team's lead pipeline.
    """

    serializer_class = EnquirySerializer
    filterset_class = EnquiryFilter
    search_fields = ["name", "email", "phone", "message"]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]
    queryset = Enquiry.objects.select_related("course").all()

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_throttles(self):
        if self.action == "create":
            return [EnquiryThrottle()]
        return super().get_throttles()

    def perform_create(self, serializer):
        enquiry = serializer.save()
        logger.info("New enquiry from %s for course=%s", enquiry.name, enquiry.course_id)
        push_notification(
            notification_type="new_enquiry",
            title="New enquiry received",
            message=f"{enquiry.name} submitted a new enquiry for {enquiry.course or 'general admission'}.",
        )

    def perform_update(self, serializer):
        enquiry = serializer.save()
        if enquiry.status == Enquiry.Status.ENROLLED:
            push_notification(
                notification_type="new_enrollment",
                title="New enrollment submitted",
                message=f"{enquiry.name} was enrolled in {enquiry.course or 'the institute'}.",
            )
