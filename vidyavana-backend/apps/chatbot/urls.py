from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import ChatMessageView, ChatSessionViewSet

router = DefaultRouter()
router.register("sessions", ChatSessionViewSet, basename="chat-session")

urlpatterns = [
    path("message/", ChatMessageView.as_view(), name="chatbot-message"),
    path("", include(router.urls)),
]
