import logging

from django.conf import settings
from django.core.mail import mail_admins
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.throttling import AnonRateThrottle

from apps.notifications.views import push_notification

from .models import ContactMessage
from .serializers import ContactMessageSerializer

logger = logging.getLogger("vidyavana")


class ContactThrottle(AnonRateThrottle):
    scope = "contact"


class ContactMessageViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    create: Public — submit the 'Contact Us' form.
    list/retrieve/update: Admin only — manage inbound messages and their status.
    """

    serializer_class = ContactMessageSerializer
    filterset_fields = ["status"]
    search_fields = ["name", "email", "subject", "message"]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]
    queryset = ContactMessage.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_throttles(self):
        if self.action == "create":
            return [ContactThrottle()]
        return super().get_throttles()

    def perform_create(self, serializer):
        ip = self.request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or self.request.META.get("REMOTE_ADDR")
        contact_message = serializer.save(ip_address=ip)
        logger.info("New contact message from %s <%s>", contact_message.name, contact_message.email)

        push_notification(
            notification_type="new_contact",
            title="New contact message",
            message=f"{contact_message.name} submitted a contact request.",
        )

        if settings.ADMIN_NOTIFICATION_EMAIL:
            try:
                mail_admins(
                    subject=f"New contact message: {contact_message.subject or 'No subject'}",
                    message=contact_message.message,
                    fail_silently=True,
                )
            except Exception:
                logger.exception("Failed to send contact notification email")
