from django.test import SimpleTestCase

from .services import detect_intent


class ChatbotIntentTests(SimpleTestCase):
    def test_detect_intent_for_greeting(self):
        self.assertEqual(detect_intent("Hello there"), "greeting")

    def test_detect_intent_for_course_enquiry(self):
        self.assertEqual(detect_intent("Tell me about Python training"), "course_enquiry")
