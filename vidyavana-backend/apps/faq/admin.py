from django.contrib import admin

from .models import FAQ, FAQCategory


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "order"]
    list_editable = ["is_active", "order"]
    search_fields = ["name"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "category", "is_active", "order"]
    list_editable = ["is_active", "order"]
    list_filter = ["is_active", "category"]
    search_fields = ["question", "answer"]
