from django.db import models

from core.models import TimeStampedModel


class SiteStatistic(TimeStampedModel):
    """
    Manually-curated statistics that cannot be derived purely from the database
    (e.g. 'Years of Experience', 'Students Trained' counted outside the system).
    Combined with live-computed counts in the dashboard API response.
    """

    class Key(models.TextChoices):
        STUDENTS_TRAINED = "students_trained", "Students Trained"
        PLACEMENTS = "placements", "Placements"
        YEARS_OF_EXPERIENCE = "years_of_experience", "Years of Experience"
        PLACEMENT_RATE = "placement_rate", "Placement Rate"
        AVERAGE_PACKAGE = "average_package", "Average Package"
        HIRING_PARTNERS = "hiring_partners", "Hiring Partners"

    key = models.CharField(max_length=50, choices=Key.choices, unique=True)
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50, help_text="Display value, e.g. '1000+', '92%', '₹4.2L'")
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Site Statistic"
        verbose_name_plural = "Site Statistics"

    def __str__(self):
        return f"{self.label}: {self.value}"
