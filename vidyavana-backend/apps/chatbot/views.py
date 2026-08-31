import logging

from django.conf import settings
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.languages.models import Language
from apps.notifications.views import push_notification

from .groq_service import transcribe_audio
from .models import ChatMessage, ChatSession
from .serializers import (
    ChatMessageInputSerializer,
    ChatMessageOutputSerializer,
    ChatSessionSerializer,
)
from .services import detect_language, generate_reply


logger = logging.getLogger("vidyavana")


class ChatbotThrottle(AnonRateThrottle):
    scope = "chatbot"


# ============================================================
# CHAT MESSAGE
# ============================================================

class ChatMessageView(APIView):
    """
    POST /api/v1/chatbot/message/

    Generates chatbot text immediately.
    Audio is handled by the browser via SpeechSynthesis.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ChatbotThrottle]

    def post(self, request):

        # ----------------------------------------------------
        # VALIDATE REQUEST
        # ----------------------------------------------------

        input_serializer = ChatMessageInputSerializer(
            data=request.data
        )

        input_serializer.is_valid(
            raise_exception=True
        )

        validated = input_serializer.validated_data

        language_code = detect_language(
            validated["message"],
            validated.get("language_code", "EN"),
        )

        # ----------------------------------------------------
        # FIND EXISTING SESSION
        # ----------------------------------------------------

        session = None

        if validated.get("session_uuid"):

            session = ChatSession.objects.filter(
                uuid=validated["session_uuid"],
                is_active=True,
            ).first()

        # ----------------------------------------------------
        # CREATE NEW SESSION
        # ----------------------------------------------------

        if session is None:

            language = Language.objects.filter(
                code=language_code
            ).first()

            session = ChatSession.objects.create(
                language=language,
                visitor_name=validated.get(
                    "visitor_name",
                    "",
                ),
                visitor_email=validated.get(
                    "visitor_email",
                    "",
                ),
            )

            logger.info(
                "New chat session started: %s",
                session.uuid,
            )

            visitor = (
                session.visitor_name
                or session.visitor_email
                or "visitor"
            )

            push_notification(
                notification_type="new_chat",
                title="New AI chat started",
                message=(
                    "A new chatbot session started for "
                    f"{visitor}."
                ),
            )

        # ----------------------------------------------------
        # SAVE USER MESSAGE
        # ----------------------------------------------------

        user_message = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.Sender.USER,
            text=validated["message"],
        )

        # ----------------------------------------------------
        # GENERATE CHATBOT TEXT
        # ----------------------------------------------------

        reply = generate_reply(
            validated["message"],
            language_code,
            session=session,
        )

        bot_text = reply["text"]

        # ----------------------------------------------------
        # SAVE BOT MESSAGE
        # ----------------------------------------------------

        bot_message = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.Sender.BOT,
            text=bot_text,
            intent=reply["intent"],
        )

        # ----------------------------------------------------
        # SERIALIZE CHAT RESPONSE
        # ----------------------------------------------------

        output = ChatMessageOutputSerializer(
            {
                "session_uuid": session.uuid,
                "user_message": user_message,
                "bot_message": bot_message,
            }
        )

        # ----------------------------------------------------
        # RETURN RESPONSE
        # ----------------------------------------------------

        return Response(
            {
                "success": True,
                "data": output.data,
            }
        )


class ChatTranscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Detailed logging for debugging transcription failures
        logger.info(
            "ChatTranscribeView.post called. "
            f"request.FILES keys: {list(request.FILES.keys())}, "
            f"request.POST keys: {list(request.POST.keys())}, "
            f"request.data: {dict(request.data)}"
        )

        audio_file = request.FILES.get("audio")
        if not audio_file:
            logger.warning(
                f"Audio file missing. Received FILES: {list(request.FILES.keys())}, "
                f"request.data type: {type(request.data)}"
            )
            return Response({"success": False, "error": "Audio file is required."}, status=400)

        logger.info(
            f"Audio file received. name={audio_file.name}, "
            f"size={audio_file.size}, "
            f"content_type={audio_file.content_type}"
        )

        if audio_file.size <= 0:
            logger.warning(f"Audio file empty: {audio_file.name}")
            return Response({"success": False, "error": "Audio file is empty."}, status=400)

        max_size = 20 * 1024 * 1024
        if audio_file.size > max_size:
            logger.warning(f"Audio file too large: {audio_file.size} bytes")
            return Response({"success": False, "error": "Audio file is too large."}, status=400)

        supported = {"audio/mpeg", "audio/wav", "audio/webm", "audio/ogg", "audio/mp4", "audio/x-wav"}
        if audio_file.content_type and audio_file.content_type not in supported:
            logger.warning(
                f"Unsupported MIME type: {audio_file.content_type}. "
                f"Supported: {supported}"
            )
            return Response({"success": False, "error": f"Unsupported audio format: {audio_file.content_type}"}, status=400)

        language_code = request.data.get("language_code") or request.data.get("language") or "en"
        logger.info(f"Language code: {language_code}")

        try:
            text = transcribe_audio(audio_file, language_code=language_code)
            logger.info(f"Transcription success. text={text[:50]}..., language={language_code}")
            return Response({"success": True, "data": {"text": text, "language_code": language_code}})
        except ValueError as exc:
            logger.warning(f"ValueError during transcription: {exc}")
            return Response({"success": False, "error": str(exc)}, status=400)
        except Exception:
            logger.exception("Groq transcription failed")
            return Response({"success": False, "error": "Sorry, I couldn't understand the audio. Please try again."}, status=500)


# ============================================================
# CHAT SESSION ADMIN VIEW
# ============================================================

class ChatSessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Admin-only chatbot conversation history.
    """

    serializer_class = ChatSessionSerializer
    permission_classes = [IsAdminUser]

    lookup_field = "uuid"

    filterset_fields = [
        "is_active",
        "language",
    ]

    search_fields = [
        "visitor_name",
        "visitor_email",
    ]

    ordering_fields = [
        "created_at",
    ]

    ordering = [
        "-created_at",
    ]

    queryset = ChatSession.objects.prefetch_related(
        "messages"
    ).all()