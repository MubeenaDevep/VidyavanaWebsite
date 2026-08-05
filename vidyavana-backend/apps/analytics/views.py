import logging

from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.views import push_notification

from .models import Lead, Visitor
from .serializers import LeadSerializer, VisitorCookieSerializer, VisitorSerializer

logger = logging.getLogger("vidyavana")


class VisitorViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = VisitorSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ["lead_status", "preferred_language"]
    search_fields = ["cookie_id", "email", "phone", "browser", "device"]
    ordering_fields = ["last_visit", "visit_count"]
    ordering = ["-last_visit"]
    queryset = Visitor.objects.all()


class VisitorCookieView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VisitorCookieSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        visitor, created = Visitor.objects.get_or_create(cookie_id=validated["cookie_id"])
        if created:
            push_notification(
                notification_type="new_visitor",
                title="New visitor tracked",
                message=f"Visitor {visitor.cookie_id} started a session.",
            )
        else:
            visitor.visit_count += 1
        visitor.browser = validated.get("browser", visitor.browser)
        visitor.device = validated.get("device", visitor.device)
        visitor.os = validated.get("os", visitor.os)
        visitor.screen_resolution = validated.get("screen_resolution", visitor.screen_resolution)
        visitor.preferred_language = validated.get("preferred_language", visitor.preferred_language)
        visitor.referrer = validated.get("referrer", visitor.referrer)
        pages = validated.get("pages_visited") or []
        if pages:
            visitor.pages_visited = pages
        visitor.last_visit = timezone.now()
        visitor.save(update_fields=[
            "browser",
            "device",
            "os",
            "screen_resolution",
            "preferred_language",
            "referrer",
            "pages_visited",
            "visit_count",
            "last_visit",
        ])

        logger.info("Visitor cookie tracked: %s", visitor.cookie_id)
        return Response({"success": True, "data": VisitorSerializer(visitor).data})


class LeadViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = LeadSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ["status"]
    search_fields = ["name", "email", "phone", "source"]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]
    queryset = Lead.objects.select_related("visitor").all()
