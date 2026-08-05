from django.contrib import admin

from .models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "course", "source", "status", "created_at"]
    list_editable = ["status"]
    list_filter = ["status", "source", "course", "created_at"]
    search_fields = ["name", "email", "phone", "message"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["course"]
