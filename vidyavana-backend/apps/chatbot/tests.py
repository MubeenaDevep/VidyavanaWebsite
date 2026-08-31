from io import BytesIO
from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework.test import APIClient

from apps.courses.models import Course, CourseCategory

from .groq_service import generate_chat_completion, transcribe_audio
from .rag.documents import _chunk_document
from .services import (
    _fallback_reply,
    _get_course_context,
    detect_intent,
    detect_language,
    generate_reply,
)


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

    def test_course_fee_uses_database_value(self):
        reply = generate_reply("How much does the AI course cost?", "EN")
        self.assertIn("12000.00", reply["text"])
        self.assertNotIn("Python Programming", reply["text"])

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

    def test_transcribe_endpoint_requires_audio(self):
        client = APIClient()
        response = client.post("/api/v1/chatbot/transcribe/", {}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("required", str(response.data).lower())
