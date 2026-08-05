from django.db import models

from core.models import PublishableModel, TimeStampedModel, UUIDModel


class FAQCategory(TimeStampedModel, PublishableModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "FAQ Category"
        verbose_name_plural = "FAQ Categories"

    def __str__(self):
        return self.name


class FAQ(TimeStampedModel, PublishableModel):
    category = models.ForeignKey(
        FAQCategory, related_name="faqs", on_delete=models.SET_NULL, null=True, blank=True
    )
    question = models.CharField(max_length=300)
    answer = models.TextField()

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class FAQQuestion(TimeStampedModel, UUIDModel):
    """A user-submitted FAQ question pending administrative review and answering."""

    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    question = models.TextField()
    is_reviewed = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "FAQ Question"
        verbose_name_plural = "FAQ Questions"
        indexes = [models.Index(fields=["is_reviewed", "created_at"])]

    def __str__(self):
        return f"FAQ Question from {self.name or 'Anonymous'}"
