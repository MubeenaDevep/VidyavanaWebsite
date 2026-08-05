from django.contrib import admin

from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["name", "role_or_course", "rating", "is_featured", "is_active", "order"]
    list_editable = ["is_featured", "is_active", "order"]
    list_filter = ["is_active", "is_featured", "rating"]
    search_fields = ["name", "role_or_course", "quote"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
