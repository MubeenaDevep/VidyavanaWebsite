from rest_framework.routers import DefaultRouter

from .views import TestimonialViewSet

router = DefaultRouter()
router.register("", TestimonialViewSet, basename="testimonial")

urlpatterns = router.urls
