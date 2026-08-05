from rest_framework import serializers

from .models import Enquiry


class EnquirySerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True, default=None)

    class Meta:
        model = Enquiry
        fields = [
            "id",
            "uuid",
            "name",
            "email",
            "phone",
            "course",
            "course_name",
            "preferred_batch_time",
            "message",
            "source",
            "status",
            "follow_up_notes",
            "created_at",
        ]
        read_only_fields = ["id", "uuid", "status", "follow_up_notes", "created_at"]

    def validate_phone(self, value):
        digits = "".join(filter(str.isdigit, value))
        if len(digits) < 7:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value
