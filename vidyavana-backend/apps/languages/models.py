from django.db import models

from core.models import PublishableModel, TimeStampedModel


class Language(TimeStampedModel, PublishableModel):
    """A language supported across the site (nav switcher, chatbot, content translations)."""

    code = models.CharField(
        max_length=5,
        unique=True,
        db_index=True,
        help_text="Short language code, e.g. EN, KN, TE",
    )
    name = models.CharField(max_length=50, help_text="Display name, e.g. English")
    native_name = models.CharField(
        max_length=50, blank=True, help_text="Name in its own script, e.g. ಕನ್ನಡ"
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Language"
        verbose_name_plural = "Languages"

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)
        if self.is_default:
            # Ensure only one default language exists
            Language.objects.exclude(pk=self.pk).update(is_default=False)
