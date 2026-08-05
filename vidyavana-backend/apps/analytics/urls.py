from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LeadViewSet, VisitorCookieView, VisitorViewSet

router = DefaultRouter()
router.register("visitors", VisitorViewSet, basename="visitor")
router.register("leads", LeadViewSet, basename="lead")

urlpatterns = [
    path("cookie/", VisitorCookieView.as_view(), name="visitor-cookie"),
    path("", include(router.urls)),
]
