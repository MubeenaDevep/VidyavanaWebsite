import logging
import threading
import uuid
from pathlib import Path

from django.conf import settings
from django.db import close_old_connections
from django.http import FileResponse, Http404
from django.urls import reverse
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.languages.models import Language
from apps.notifications.views import push_notification

from .groq_service import transcribe_audio
from .models import ChatMessage, ChatSession, TTSAudio
from .serializers import (
    ChatMessageInputSerializer,
    ChatMessageOutputSerializer,
    ChatSessionSerializer,
)
from .services import detect_language, generate_reply
from .tts_service import clean_text_for_speech


logger = logging.getLogger("vidyavana")


def _audio_url(filename: str) -> str:
    return reverse("chatbot-audio-file", kwargs={"filename": filename})


def _generate_tts_in_background(audio_id, text: str, language_code: str, filename: str):
    """Generate audio after the response has been returned to the client."""

    from .tts_service import generate_speech

    close_old_connections()
    try:
        audio_path = generate_speech(text, language_code, filename=filename)
        TTSAudio.objects.filter(pk=audio_id).update(
            status=TTSAudio.Status.READY,
            error_message="",
        )
        logger.info("Background TTS ready: %s", audio_path)
    except Exception as exc:
        TTSAudio.objects.filter(pk=audio_id).update(
            status=TTSAudio.Status.ERROR,
            error_message=str(exc)[:255],
        )
        logger.exception("Background TTS generation failed")
    finally:
        close_old_connections()


def _queue_tts(text: str, language_code: str) -> tuple[TTSAudio, str]:
    filename = f"{uuid.uuid4().hex}.mp3"
    audio = TTSAudio.objects.create(
        filename=filename,
        status=TTSAudio.Status.PROCESSING,
    )
    audio_url = _audio_url(filename)
    threading.Thread(
        target=_generate_tts_in_background,
        args=(audio.pk, text, language_code, filename),
        name=f"chatbot-tts-{audio.pk}",
        daemon=True,
    ).start()
    return audio, audio_url


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
        # QUEUE TTS AUDIO WITHOUT BLOCKING THE RESPONSE
        # ----------------------------------------------------
        try:
            speech_text = clean_text_for_speech(bot_text)
            audio, audio_url = _queue_tts(speech_text, language_code)
        except Exception:
            logger.exception("TTS queueing failed")
            audio = None
            audio_url = None

        # ----------------------------------------------------
        # SERIALIZE CHAT RESPONSE
        # ----------------------------------------------------

        output = ChatMessageOutputSerializer(
            {
                "session_uuid": session.uuid,
                "user_message": user_message,
                "bot_message": bot_message,
                "audio_url": None,
                "audio": (
                    {
                        "status": audio.status,
                        "url": audio_url,
                    }
                    if audio
                    else None
                ),
                "cta": reply.get("cta"),
            }
        )

        return Response(
            {
                "success": True,
                "data": output.data,
            }
        )


class ChatAudioStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, filename):
        audio = TTSAudio.objects.filter(filename=filename).first()
        if audio is None:
            return Response({"status": "error", "url": None}, status=404)

        return Response(
            {
                "status": audio.status,
                "url": _audio_url(audio.filename)
                if audio.status == TTSAudio.Status.READY
                else None,
                "error": audio.error_message or None,
            }
        )


class ChatAudioFileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, filename):
        audio = TTSAudio.objects.filter(
            filename=filename,
            status=TTSAudio.Status.READY,
        ).first()
        if audio is None:
            raise Http404

        if (
            not filename.endswith(".mp3")
            or Path(filename).name != filename
            or "/" in filename
            or "\\" in filename
        ):
            raise Http404

        media_root = Path(settings.MEDIA_ROOT).resolve()
        try:
            tts_directory = (media_root / "tts").resolve(strict=True)
            tts_directory.relative_to(media_root)
            audio_path = (tts_directory / filename).resolve(strict=True)
            audio_path.relative_to(tts_directory)
        except (OSError, ValueError):
            raise Http404 from None

        if not audio_path.is_file():
            raise Http404

        return FileResponse(audio_path.open("rb"), content_type="audio/mpeg")


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