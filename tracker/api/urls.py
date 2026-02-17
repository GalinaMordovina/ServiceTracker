from rest_framework.routers import DefaultRouter

from tracker.api.views import (
    EmployeeViewSet,
    TaskViewSet,
    AnalyticsViewSet,
)


router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employees")
router.register("tasks", TaskViewSet, basename="tasks")
router.register("analytics", AnalyticsViewSet, basename="analytics")

# готовый список urlpattern'ов
urlpatterns = router.urls
