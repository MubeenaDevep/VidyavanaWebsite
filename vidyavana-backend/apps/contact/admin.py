from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "subject", "status", "created_at"]
    list_editable = ["status"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "email", "phone", "subject", "message"]
    readonly_fields = ["uuid", "ip_address", "created_at", "updated_at"]
