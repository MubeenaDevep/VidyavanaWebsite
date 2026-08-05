from rest_framework import serializers

from .models import ChatMessage, ChatSession


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "sender", "text", "intent", "created_at"]
        read_only_fields = ["id", "sender", "intent", "created_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            "id",
            "uuid",
            "language",
            "visitor_name",
            "visitor_email",
            "is_active",
            "messages",
            "created_at",
        ]
        read_only_fields = ["id", "uuid", "created_at"]


class ChatMessageInputSerializer(serializers.Serializer):
    """Request payload for POST /chatbot/message/."""

    session_uuid = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField(max_length=1000)
    language_code = serializers.CharField(max_length=5, required=False, default="EN")
    visitor_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    visitor_email = serializers.EmailField(required=False, allow_blank=True)

    def validate_message(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Message cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Message is too long (max 1000 characters).")
        return value


class ChatMessageOutputSerializer(serializers.Serializer):
    session_uuid = serializers.UUIDField()
    user_message = ChatMessageSerializer()
    bot_message = ChatMessageSerializer()
