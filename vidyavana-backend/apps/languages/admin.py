from django.contrib import admin

from .models import Language


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "native_name", "is_default", "is_active", "order"]
    list_editable = ["is_default", "is_active", "order"]
    search_fields = ["name", "code", "native_name"]
    list_filter = ["is_active", "is_default"]
    ordering = ["order"]
