from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationReadView, NotificationViewSet

router = DefaultRouter()
router.register("", NotificationViewSet, basename="notification")

urlpatterns = [
    path("<uuid:uuid>/read/", NotificationReadView.as_view(), name="notification-read"),
    path("", include(router.urls)),
]
