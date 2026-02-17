from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


@extend_schema(exclude=True)  # исключаем из OpenAPI
class HealthCheckView(APIView):
    """Проверка работоспособности API."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        _ = request  # чтобы не висело предупреждения (в след ветке продолжу)
        return Response({"status": "ok"})
