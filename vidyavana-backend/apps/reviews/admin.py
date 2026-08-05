from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["name", "course", "rating", "is_approved", "created_at"]
    list_editable = ["is_approved"]
    list_filter = ["is_approved", "rating", "course"]
    search_fields = ["name", "email", "title", "message"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    actions = ["approve_reviews", "reject_reviews"]

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} review(s) approved.")

    @admin.action(description="Reject (unapprove) selected reviews")
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} review(s) rejected.")
