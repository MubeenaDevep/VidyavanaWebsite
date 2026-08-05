from rest_framework import serializers

from .models import Lead, Visitor


class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = [
            "id",
            "uuid",
            "cookie_id",
            "browser",
            "device",
            "os",
            "screen_resolution",
            "preferred_language",
            "referrer",
            "pages_visited",
            "visit_count",
            "first_visit",
            "last_visit",
            "email",
            "phone",
            "lead_status",
            "created_at",
        ]
        read_only_fields = ["id", "uuid", "first_visit", "last_visit", "created_at"]


class VisitorCookieSerializer(serializers.Serializer):
    cookie_id = serializers.CharField(max_length=128)
    browser = serializers.CharField(max_length=80, required=False, allow_blank=True)
    device = serializers.CharField(max_length=80, required=False, allow_blank=True)
    os = serializers.CharField(max_length=80, required=False, allow_blank=True)
    screen_resolution = serializers.CharField(max_length=40, required=False, allow_blank=True)
    preferred_language = serializers.CharField(max_length=8, required=False, allow_blank=True)
    referrer = serializers.URLField(required=False, allow_blank=True)
    pages_visited = serializers.ListField(child=serializers.CharField(), required=False)
    visit_count = serializers.IntegerField(required=False, min_value=1)


class LeadSerializer(serializers.ModelSerializer):
    visitor_cookie_id = serializers.CharField(source="visitor.cookie_id", read_only=True, default=None)

    class Meta:
        model = Lead
        fields = [
            "id",
            "uuid",
            "visitor",
            "visitor_cookie_id",
            "name",
            "email",
            "phone",
            "source",
            "status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "uuid", "created_at"]
