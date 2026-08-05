from rest_framework import serializers

from .models import Language


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            "id",
            "code",
            "name",
            "native_name",
            "is_default",
            "is_active",
            "order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_code(self, value):
        value = value.upper().strip()
        if len(value) < 2:
            raise serializers.ValidationError("Language code must be at least 2 characters.")
        return value
