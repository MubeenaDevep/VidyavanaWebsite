from django.contrib import admin

from .models import Course, CourseCategory


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "order"]
    list_editable = ["is_active", "order"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "tagline"]
    list_filter = ["is_active"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "level", "duration", "fee", "is_featured", "is_active", "order"]
    list_editable = ["is_featured", "is_active", "order"]
    list_filter = ["category", "level", "is_active", "is_featured", "certificate_included"]
    search_fields = ["name", "short_description", "description"]
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ["category"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
