from django.db import models

from apps.languages.models import Language
from core.models import TimeStampedModel, UUIDModel


class ChatSession(TimeStampedModel, UUIDModel):
    """A single visitor's conversation with the AI assistant."""

    language = models.ForeignKey(
        Language, related_name="chat_sessions", on_delete=models.SET_NULL, null=True, blank=True
    )
    visitor_name = models.CharField(max_length=100, blank=True)
    visitor_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"

    def __str__(self):
        return f"Session {self.uuid}"


class ChatMessage(TimeStampedModel):
    class Sender(models.TextChoices):
        USER = "user", "User"
        BOT = "bot", "Bot"

    session = models.ForeignKey(ChatSession, related_name="messages", on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=Sender.choices)
    text = models.TextField()
    intent = models.CharField(
        max_length=50, blank=True, help_text="Detected intent, e.g. 'course_enquiry', 'greeting'"
    )

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

    def __str__(self):
        return f"[{self.sender}] {self.text[:40]}"
