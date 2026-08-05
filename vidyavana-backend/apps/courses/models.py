from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from core.models import PublishableModel, TimeStampedModel, UUIDModel


class CourseCategory(TimeStampedModel, PublishableModel):
    """A top-level course grouping, e.g. 'Web Development', 'Programming Courses'."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    tagline = models.CharField(max_length=200, blank=True)
    icon = models.CharField(
        max_length=50, blank=True, help_text="Icon identifier used by the frontend (e.g. lucide icon name)"
    )

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Course Category"
        verbose_name_plural = "Course Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(TimeStampedModel, PublishableModel, UUIDModel):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    category = models.ForeignKey(
        CourseCategory, related_name="courses", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    short_description = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=50, help_text="e.g. '3 Months', '6 Weeks'")
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    fee = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    image = models.ImageField(upload_to="courses/", blank=True, null=True)
    certificate_included = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        indexes = [
            models.Index(fields=["level", "is_active"]),
            models.Index(fields=["is_featured", "is_active"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
