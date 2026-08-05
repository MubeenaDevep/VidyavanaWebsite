from django.core.validators import RegexValidator
from django.db import models

from core.models import TimeStampedModel, UUIDModel

phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-()]{7,15}$", message="Enter a valid phone number."
)


class ContactMessage(TimeStampedModel, UUIDModel):
    """A general 'Contact Us' form submission."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, validators=[phone_validator])
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return f"{self.name} — {self.subject or 'No subject'}"
