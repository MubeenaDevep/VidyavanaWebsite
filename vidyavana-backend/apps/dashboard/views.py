import logging

from django.db.models import Avg
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.contact.models import ContactMessage
from apps.courses.models import Course, CourseCategory
from apps.enquiry.models import Enquiry
from apps.languages.models import Language
from apps.reviews.models import Review
from apps.testimonials.models import Testimonial
from core.permissions import IsAdminOrReadOnly

from .models import SiteStatistic
from .serializers import (
    AdminDashboardSummarySerializer,
    DashboardSummarySerializer,
    SiteStatisticSerializer,
)

logger = logging.getLogger("vidyavana")


class SiteStatisticViewSet(ModelViewSet):
    """Admin-manageable manual statistics (public read, admin write)."""

    serializer_class = SiteStatisticSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["is_active", "key"]
    ordering_fields = ["order"]
    ordering = ["order"]

    def get_queryset(self):
        qs = SiteStatistic.objects.all()
        if self.request.method == "GET" and not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs


def _base_summary():
    approved_reviews = Review.objects.filter(is_approved=True)
    return {
        "manual_statistics": SiteStatistic.objects.filter(is_active=True),
        "courses_offered": Course.objects.filter(is_active=True).count(),
        "course_categories": CourseCategory.objects.filter(is_active=True).count(),
        "total_reviews": approved_reviews.count(),
        "average_rating": round(approved_reviews.aggregate(avg=Avg("rating"))["avg"] or 0, 2),
        "total_testimonials": Testimonial.objects.filter(is_active=True).count(),
        "languages_supported": Language.objects.filter(is_active=True).count(),
    }


class DashboardStatsView(APIView):
    """
    GET /api/v1/dashboard/stats/
    Public homepage statistics (student counts, ratings, course counts, etc.).
    """

    permission_classes = [AllowAny]

    def get(self, request):
        data = _base_summary()
        serializer = DashboardSummarySerializer(data)
        logger.info("Dashboard public stats requested")
        return Response({"success": True, "data": serializer.data})


class AdminDashboardStatsView(APIView):
    """
    GET /api/v1/dashboard/admin-stats/
    Staff-only operational overview: pending enquiries, unread messages, moderation queue.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        data = _base_summary()
        data.update(
            {
                "new_enquiries": Enquiry.objects.filter(status=Enquiry.Status.NEW).count(),
                "total_enquiries": Enquiry.objects.count(),
                "new_contact_messages": ContactMessage.objects.filter(
                    status=ContactMessage.Status.NEW
                ).count(),
                "pending_reviews": Review.objects.filter(is_approved=False).count(),
            }
        )
        serializer = AdminDashboardSummarySerializer(data)
        logger.info("Dashboard admin stats requested by %s", request.user)
        return Response({"success": True, "data": serializer.data})
