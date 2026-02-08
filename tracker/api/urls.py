from rest_framework.routers import DefaultRouter

from tracker.api.views import EmployeeViewSet

# Роутер сам создаст все CRUD-эндпоинты для EmployeeViewSet
router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employees")

# готовый список urlpattern'ов
urlpatterns = router.urls
