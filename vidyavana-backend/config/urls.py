from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

api_v1_patterns = [
    path("accounts/", include("apps.accounts.urls")),
    path("languages/", include("apps.languages.urls")),
    path("courses/", include("apps.courses.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("testimonials/", include("apps.testimonials.urls")),
    path("contact/", include("apps.contact.urls")),
    path("enquiry/", include("apps.enquiry.urls")),
    path("faq/", include("apps.faq.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("chatbot/", include("apps.chatbot.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("notifications/", include("apps.notifications.urls")),

    # JWT auth (architecture ready for admin / staff clients)
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # API documentation
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
