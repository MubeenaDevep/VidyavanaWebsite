from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (
    ChatAudioFileView,
    ChatAudioStatusView,
    ChatMessageView,
    ChatSessionViewSet,
    ChatTranscribeView,
)

router = DefaultRouter()
router.register("sessions", ChatSessionViewSet, basename="chat-session")

urlpatterns = [
    path("message/", ChatMessageView.as_view(), name="chatbot-message"),
    path("audio/<str:filename>/", ChatAudioStatusView.as_view(), name="chatbot-audio-status"),
    path("audio-file/<str:filename>/", ChatAudioFileView.as_view(), name="chatbot-audio-file"),
    path("transcribe/", ChatTranscribeView.as_view(), name="chatbot-transcribe"),
    path("", include(router.urls)),
]
