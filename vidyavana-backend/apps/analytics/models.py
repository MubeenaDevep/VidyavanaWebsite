from django.db import models

from core.models import TimeStampedModel, UUIDModel


class Visitor(TimeStampedModel, UUIDModel):
    cookie_id = models.CharField(max_length=128, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    browser = models.CharField(max_length=80, blank=True)
    device = models.CharField(max_length=80, blank=True)
    os = models.CharField(max_length=80, blank=True)
    screen_resolution = models.CharField(max_length=40, blank=True)
    timezone = models.CharField(max_length=64, blank=True)
    preferred_language = models.CharField(max_length=8, blank=True)
    referrer = models.URLField(blank=True)
    pages_visited = models.JSONField(default=list, blank=True)
    visit_count = models.PositiveIntegerField(default=1)
    first_visit = models.DateTimeField(auto_now_add=True)
    last_visit = models.DateTimeField(auto_now=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    lead_status = models.CharField(
        max_length=24,
        default="new",
        blank=True,
    )

    class Meta:
        ordering = ["-last_visit"]
        verbose_name = "Visitor"
        verbose_name_plural = "Visitors"

    def __str__(self):
        return self.cookie_id


class Lead(TimeStampedModel, UUIDModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        INTERESTED = "interested", "Interested"
        FOLLOW_UP = "follow_up", "Follow Up"
        ENROLLED = "enrolled", "Enrolled"
        CLOSED = "closed", "Closed"

    visitor = models.ForeignKey(Visitor, related_name="leads", on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    source = models.CharField(max_length=40, default="website")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.NEW, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lead"
        verbose_name_plural = "Leads"

    def __str__(self):
        return f"{self.name} ({self.status})"
