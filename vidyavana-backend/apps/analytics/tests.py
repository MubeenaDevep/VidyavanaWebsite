from django.test import TestCase
from rest_framework.test import APIClient


class VisitorCookieAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_visitor_cookie_endpoint(self):
        payload = {
            "cookie_id": "cookie-123",
            "browser": "Chrome",
            "device": "Desktop",
            "os": "Windows",
            "screen_resolution": "1366x768",
            "preferred_language": "EN",
            "pages_visited": ["/", "/courses/"],
            "visit_count": 2,
        }
        response = self.client.post("/api/v1/analytics/cookie/", payload, format="json")
        self.assertEqual(response.status_code, 200)
 