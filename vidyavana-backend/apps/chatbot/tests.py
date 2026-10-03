from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.courses.models import Course, CourseCategory

from .groq_service import generate_chat_completion, transcribe_audio
from .models import ChatMessage, ChatSession, TTSAudio
from .rag.documents import _chunk_document
from .services import (
    _fallback_reply,
    _get_course_context,
    detect_intent,
    detect_language,
    generate_reply,
)
from .tts_service import clean_text_for_speech


class ChatbotIntentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = CourseCategory.objects.create(name="Programming")
        Course.objects.create(
            category=category,
            name="AI Fundamentals",
            short_description="Learn artificial intelligence basics.",
            description="Python, machine learning, and model fundamentals.",
            duration="6 Months",
            fee="12000.00",
            is_active=True,
        )
        Course.objects.create(
            category=category,
            name="Python Programming",
            short_description="Learn Python programming.",
            duration="3 Months",
            fee="8000.00",
            is_active=True,
        )

    def test_detect_intent_for_greeting(self):
        self.assertEqual(detect_intent("Hello there"), "greeting")

    def test_detect_intent_for_course_enquiry(self):
        self.assertEqual(detect_intent("Tell me about Python training"), "course_enquiry")

    def test_institute_answers_include_contact_cta(self):
        reply = generate_reply("Where is Vidyavana located?", "EN")
        self.assertIn("R.N. Street", reply["text"])
        self.assertEqual(reply["cta"]["href"], "#contact")

    def test_certificate_and_audience_are_institute_questions(self):
        self.assertEqual(detect_intent("Do you provide certificates?"), "institute_enquiry")
        self.assertEqual(detect_intent("Who can join?"), "institute_enquiry")

    def test_fee_reply_never_exposes_course_fee(self):
        reply = generate_reply("How much does the AI course cost?", "EN")
        self.assertIn("not currently available", reply["text"])
        self.assertNotIn("12000.00", reply["text"])

    def test_course_follow_up_uses_session_context(self):
        session = ChatSession.objects.create()
        ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.Sender.USER,
            text="Tell me about the AI course",
        )
        reply = generate_reply("How long is it?", "EN", session=session)
        self.assertIn("6 Months", reply["text"])

    def test_detect_language_from_kannada_script(self):
        self.assertEqual(detect_language("ನಮಸ್ಕಾರ! ನೀವು ಹೇಗಿದ್ದೀರಿ?", "EN"), "KN")

    def test_detect_language_from_telugu_script(self):
        self.assertEqual(detect_language("నమస్కారం! మీరు ఎలా ఉన్నారు?", "EN"), "TE")

    def test_kannada_greeting_fallback_is_kannada(self):
        reply = _fallback_reply("ನಮಸ್ಕಾರ", "KN", "greeting")
        self.assertIn("ನಮಸ್ಕಾರ", reply["text"])

    def test_rag_document_chunk_preserves_source_and_section(self):
        chunks = _chunk_document(
            "faq.txt",
            "Fees:\nCurrent fees are unavailable.\n\n"
            "Payment:\nOnline payment is unavailable.",
        )
        self.assertEqual(chunks[0]["source"], "faq.txt")
        self.assertEqual(chunks[0]["section"], "Fees")
        self.assertIn("Current fees", chunks[0]["text"])

    @patch("apps.chatbot.services.retrieve_context", return_value="Verified training information")
    @patch("apps.chatbot.services._fallback_reply", return_value={"text": "fallback", "intent": "general"})
    def test_rag_context_does_not_break_fallback(
        self,
        mock_fallback_reply,
        mock_retrieve_context,
    ):
        reply = generate_reply("What training approach do you use?", "EN")
        self.assertIn("text", reply)

    def test_english_duration_retrieves_only_ai_course(self):
        context = _get_course_context("How long is the AI course?", "course_enquiry")
        self.assertIn("Course: AI Fundamentals", context)
        self.assertIn("Duration: 6 Months", context)
        self.assertNotIn("Course: Python Programming", context)

    def test_kannada_duration_returns_ai_duration(self):
        reply = generate_reply("AI ಕೋರ್ಸ್ ಎಷ್ಟು ತಿಂಗಳು?", "EN")
        self.assertEqual(reply["intent"], "course_enquiry")
        self.assertIn("6 Months", reply["text"])
        self.assertIn("ಕೋರ್ಸ್", reply["text"])

    def test_telugu_duration_returns_ai_duration(self):
        reply = generate_reply("AI కోర్సు ఎంత కాలం?", "EN")
        self.assertEqual(reply["intent"], "course_enquiry")
        self.assertIn("6 Months", reply["text"])
        self.assertIn("కోర్సు", reply["text"])

    def test_syllabus_question_retrieves_specific_course_context(self):
        context = _get_course_context("What is the syllabus for Python?", "course_enquiry")
        self.assertIn("Course: Python Programming", context)
        self.assertIn("Python programming", context)
        self.assertNotIn("Course: AI Fundamentals", context)

    def test_general_course_question_returns_catalog(self):
        context = _get_course_context("What courses are available?", "course_enquiry")
        self.assertIn("Course: AI Fundamentals", context)
        self.assertIn("Course: Python Programming", context)

    def test_unknown_course_does_not_return_catalog(self):
        context = _get_course_context("How long is the Robotics course?", "course_enquiry")
        self.assertEqual(context, "")

    @patch("apps.chatbot.groq_service._get_groq_client")
    def test_groq_provider_returns_text(self, mock_get_client):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Groq reply"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        reply = generate_chat_completion(
            system_prompt="Answer clearly.",
            history=[],
            user_message="What courses are available?",
            rag_context="Course list available",
        )

        self.assertEqual(reply, "Groq reply")
        mock_client.chat.completions.create.assert_called_once()

    @patch("apps.chatbot.groq_service._get_groq_client")
    def test_groq_transcription_returns_text(self, mock_get_client):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "What courses are available?"
        mock_client.audio.transcriptions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        audio = BytesIO(b"fake-audio-bytes")
        audio.name = "voice.wav"
        text = transcribe_audio(audio, language_code="en")

        self.assertEqual(text, "What courses are available?")
        mock_client.audio.transcriptions.create.assert_called_once()

    def test_ready_tts_audio_is_served_from_the_chatbot_endpoint(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                filename = "ready-audio.mp3"
                audio_path = Path(media_root) / "tts" / filename
                audio_path.parent.mkdir()
                audio_path.write_bytes(b"mp3-audio")
                TTSAudio.objects.create(
                    filename=filename,
                    status=TTSAudio.Status.READY,
                )
                client = APIClient()

                status_response = client.get(f"/api/v1/chatbot/audio/{filename}/")
                file_response = client.get(f"/api/v1/chatbot/audio-file/{filename}/")
                try:
                    audio_content = b"".join(file_response.streaming_content)
                finally:
                    file_response.close()

        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(
            status_response.data["url"],
            f"/api/v1/chatbot/audio-file/{filename}/",
        )
        self.assertEqual(file_response.status_code, 200)
        self.assertEqual(file_response["Content-Type"], "audio/mpeg")
        self.assertEqual(audio_content, b"mp3-audio")

    def test_tts_file_endpoint_rejects_non_ready_audio(self):
        TTSAudio.objects.create(
            filename="processing-audio.mp3",
            status=TTSAudio.Status.PROCESSING,
        )

        response = APIClient().get("/api/v1/chatbot/audio-file/processing-audio.mp3/")

        self.assertEqual(response.status_code, 404)

    def test_transcribe_endpoint_requires_audio(self):
        client = APIClient()
        response = client.post("/api/v1/chatbot/transcribe/", {}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("required", str(response.data).lower())

    def test_clean_text_for_speech_removes_markdown_formatting(self):
        raw = "**Course Details**\n\n* Duration: 3 months\n* Mode: Offline\n\n[Learn more](https://example.com)"
        cleaned = clean_text_for_speech(raw)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("[Learn more]", cleaned)
        self.assertIn("Course Details", cleaned)
        self.assertIn("Duration: 3 months", cleaned)
        self.assertIn("Mode: Offline", cleaned)

    @patch("apps.chatbot.services.generate_chat_completion", return_value="Python is a programming language.")
    @patch("apps.chatbot.services.retrieve_context", return_value="Python course details at Vidyavana")
    def test_general_question_ignores_irrelevant_rag_context(
        self,
        mock_retrieve_context,
        mock_generate,
    ):
        reply = generate_reply("What is Python?", "EN")
        self.assertEqual(reply["text"], "Python is a programming language.")
        mock_retrieve_context.assert_called_once()
        self.assertEqual(mock_generate.call_args.kwargs["rag_context"], "")
