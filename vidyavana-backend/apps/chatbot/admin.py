from django.contrib import admin

from .models import ChatMessage, ChatSession


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ["sender", "text", "intent", "created_at"]
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["uuid", "visitor_name", "language", "is_active", "created_at"]
    list_filter = ["is_active", "language"]
    search_fields = ["visitor_name", "visitor_email", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    inlines = [ChatMessageInline]
