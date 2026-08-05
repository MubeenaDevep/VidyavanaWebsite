from rest_framework import serializers

from .models import SiteStatistic


class SiteStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteStatistic
        fields = ["id", "key", "label", "value", "icon", "is_active", "order"]
        read_only_fields = ["id"]


class DashboardSummarySerializer(serializers.Serializer):
    """Read-only aggregate response for the public dashboard/homepage stats endpoint."""

    manual_statistics = SiteStatisticSerializer(many=True)
    courses_offered = serializers.IntegerField()
    course_categories = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    total_testimonials = serializers.IntegerField()
    languages_supported = serializers.IntegerField()


class AdminDashboardSummarySerializer(DashboardSummarySerializer):
    """Extends the public summary with internal, staff-only figures."""

    new_enquiries = serializers.IntegerField()
    total_enquiries = serializers.IntegerField()
    new_contact_messages = serializers.IntegerField()
    pending_reviews = serializers.IntegerField()
