from django.contrib.auth import get_user_model
from django.db import models

from core.models import TimeStampedModel

User = get_user_model()


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    preferred_language = models.CharField(max_length=5, default="EN")
    timezone = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return str(self.user)
