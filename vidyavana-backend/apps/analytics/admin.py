from django.contrib import admin

from .models import Lead, Visitor


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ["cookie_id", "browser", "device", "screen_resolution", "visit_count", "last_visit"]
    search_fields = ["cookie_id", "email", "phone"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "status", "source", "created_at"]
    list_filter = ["status", "source"]
    search_fields = ["name", "email", "phone"]
