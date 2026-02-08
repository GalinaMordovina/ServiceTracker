from rest_framework.routers import DefaultRouter

from tracker.api.views import EmployeeViewSet, TaskViewSet


router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employees")
router.register("tasks", TaskViewSet, basename="tasks")

# готовый список urlpattern'ов
urlpatterns = router.urls
