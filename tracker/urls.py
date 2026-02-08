from django.urls import path, include

from tracker.views import HealthCheckView


urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("", include("tracker.api.urls")),  # подключаем все DRF-роуты
]
