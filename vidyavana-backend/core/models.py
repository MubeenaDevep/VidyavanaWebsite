import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model providing created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Abstract base model with a UUID public identifier alongside the PK."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """Abstract base model for content that can be toggled active/inactive and ordered."""

    is_active = models.BooleanField(default=True, db_index=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["order", "-created_at"]
