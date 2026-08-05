from django.core.validators import RegexValidator
from django.db import models

from apps.courses.models import Course
from core.models import TimeStampedModel, UUIDModel

phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-()]{7,15}$", message="Enter a valid phone number."
)


class Enquiry(TimeStampedModel, UUIDModel):
    """A course-interest / admission enquiry lead, e.g. from an 'Enroll Now' form."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        ENROLLED = "enrolled", "Enrolled"
        CLOSED = "closed", "Closed"

    class Source(models.TextChoices):
        WEBSITE = "website", "Website"
        CHATBOT = "chatbot", "Chatbot"
        PHONE = "phone", "Phone"
        WALK_IN = "walk_in", "Walk-in"
        OTHER = "other", "Other"

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, validators=[phone_validator])
    course = models.ForeignKey(
        Course, related_name="enquiries", on_delete=models.SET_NULL, null=True, blank=True
    )
    preferred_batch_time = models.CharField(max_length=50, blank=True, help_text="e.g. Morning, Evening, Weekend")
    message = models.TextField(blank=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.WEBSITE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    follow_up_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Enquiry"
        verbose_name_plural = "Enquiries"
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return f"{self.name} — {self.course or 'General'}"
