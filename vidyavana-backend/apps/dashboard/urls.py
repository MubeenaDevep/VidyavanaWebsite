from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import AdminDashboardStatsView, DashboardStatsView, SiteStatisticViewSet

router = DefaultRouter()
router.register("statistics", SiteStatisticViewSet, basename="site-statistic")

urlpatterns = [
    path("stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("admin-stats/", AdminDashboardStatsView.as_view(), name="dashboard-admin-stats"),
    path("", include(router.urls)),
]
