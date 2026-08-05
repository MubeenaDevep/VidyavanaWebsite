from rest_framework.routers import DefaultRouter

from .views import FAQCategoryViewSet, FAQQuestionViewSet, FAQViewSet

router = DefaultRouter()
router.register("categories", FAQCategoryViewSet, basename="faq-category")
router.register("", FAQViewSet, basename="faq")
router.register("questions", FAQQuestionViewSet, basename="faq-question")

urlpatterns = router.urls
