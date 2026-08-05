from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.courses.models import Course
from core.models import TimeStampedModel, UUIDModel


class Review(TimeStampedModel, UUIDModel):
    """A star-rated review left by a student, optionally tied to a specific course."""

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    course = models.ForeignKey(
        Course, related_name="reviews", on_delete=models.SET_NULL, null=True, blank=True
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    is_approved = models.BooleanField(
        default=False, db_index=True, help_text="Only approved reviews are shown publicly."
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        indexes = [models.Index(fields=["is_approved", "rating"])]

    def __str__(self):
        return f"{self.name} — {self.rating}★"
