from django.db import models

from core.models import TimeStampedModel, UUIDModel


class Notification(TimeStampedModel, UUIDModel):
    class Type(models.TextChoices):
        NEW_VISITOR = "new_visitor", "New Visitor"
        NEW_CHAT = "new_chat", "New Chat"
        NEW_CONTACT = "new_contact", "New Contact"
        NEW_ENQUIRY = "new_enquiry", "New Enquiry"
        NEW_ENROLLMENT = "new_enrollment", "New Enrollment"
        SYSTEM = "system", "System"

    type = models.CharField(max_length=24, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField(max_length=120)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.title} ({self.type})"
