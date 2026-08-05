import logging

from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.languages.models import Language

from apps.notifications.views import push_notification

from .models import ChatMessage, ChatSession
from .serializers import (
    ChatMessageInputSerializer,
    ChatMessageOutputSerializer,
    ChatSessionSerializer,
)
from .services import generate_reply

logger = logging.getLogger("vidyavana")


class ChatbotThrottle(AnonRateThrottle):
    scope = "chatbot"


class ChatMessageView(APIView):
    """
    POST /api/v1/chatbot/message/
    Send a message to the AI assistant. Creates a session on first call
    (when session_uuid is omitted), then continues that session on
    subsequent calls.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ChatbotThrottle]

    def post(self, request):
        input_serializer = ChatMessageInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        session = None
        if validated.get("session_uuid"):
            session = ChatSession.objects.filter(uuid=validated["session_uuid"], is_active=True).first()

        if session is None:
            language = Language.objects.filter(code=validated.get("language_code", "EN").upper()).first()
            session = ChatSession.objects.create(
                language=language,
                visitor_name=validated.get("visitor_name", ""),
                visitor_email=validated.get("visitor_email", ""),
            )
            logger.info("New chat session started: %s", session.uuid)
            push_notification(
                notification_type="new_chat",
                title="New AI chat started",
                message=f"A new chatbot session started for {session.visitor_name or session.visitor_email or 'visitor'}.",
            )

        user_message = ChatMessage.objects.create(
            session=session, sender=ChatMessage.Sender.USER, text=validated["message"]
        )

        reply = generate_reply(
            validated["message"],
            validated.get("language_code", "EN"),
            session=session,
        )
        bot_message = ChatMessage.objects.create(
            session=session, sender=ChatMessage.Sender.BOT, text=reply["text"], intent=reply["intent"]
        )

        output = ChatMessageOutputSerializer(
            {
                "session_uuid": session.uuid,
                "user_message": user_message,
                "bot_message": bot_message,
            }
        )
        return Response({"success": True, "data": output.data})


class ChatSessionViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Admin-only: browse chatbot conversation history / transcripts."""

    serializer_class = ChatSessionSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "uuid"
    filterset_fields = ["is_active", "language"]
    search_fields = ["visitor_name", "visitor_email"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    queryset = ChatSession.objects.prefetch_related("messages").all()
