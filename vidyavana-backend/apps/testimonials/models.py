from django.db import models

from apps.courses.models import Course
from core.models import PublishableModel, TimeStampedModel, UUIDModel


class Testimonial(TimeStampedModel, PublishableModel, UUIDModel):
    """A curated homepage testimonial (student photo + quote), independent of raw reviews."""

    name = models.CharField(max_length=100)
    role_or_course = models.CharField(
        max_length=150, blank=True, help_text="e.g. 'Web Development Graduate'"
    )
    course = models.ForeignKey(
        Course, related_name="testimonials", on_delete=models.SET_NULL, null=True, blank=True
    )
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    is_featured = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.name} — {self.role_or_course or 'Testimonial'}"
