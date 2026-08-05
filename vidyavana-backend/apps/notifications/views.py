import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger("vidyavana")


class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["type", "is_read"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    queryset = Notification.objects.all()

    def get_queryset(self):
        return Notification.objects.all()


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):
        notification = Notification.objects.get(uuid=uuid)
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response({"success": True, "data": NotificationSerializer(notification).data})


def push_notification(notification_type, title, message):
    notification = Notification.objects.create(type=notification_type, title=title, message=message)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "send_notification",
            "notification": NotificationSerializer(notification).data,
        },
    )
    logger.info("Notification pushed: %s", notification.title)
    return notification
