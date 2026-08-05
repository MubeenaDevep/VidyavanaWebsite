from django.test import TestCase
from rest_framework.test import APIClient

from .models import ContactMessage


class ContactAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_contact_create_endpoint(self):
        payload = {
            "name": "Test User",
            "email": "user@example.com",
            "phone": "+91 9876543210",
            "subject": "Course Enquiry",
            "message": "I want to know more about your web development program.",
        }
        response = self.client.post("/api/v1/contact/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ContactMessage.objects.filter(email="user@example.com").exists())
