from django.contrib import admin

from .models import SiteStatistic


@admin.register(SiteStatistic)
class SiteStatisticAdmin(admin.ModelAdmin):
    list_display = ["label", "key", "value", "is_active", "order"]
    list_editable = ["value", "is_active", "order"]
    list_filter = ["is_active"]
    search_fields = ["label", "key"]
