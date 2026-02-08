from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter

from tracker.models import Employee
from tracker.api.serializers import EmployeeSerializer


class EmployeeViewSet(ModelViewSet):
    """
    ViewSet для CRUD-операций с сотрудниками.
    ModelViewSet автоматически реализует:
    - list   (GET /employees/)
    - create (POST /employees/)
    - retrieve (GET /employees/{id}/)
    - update (PUT /employees/{id}/)
    - partial_update (PATCH /employees/{id}/)
    - destroy (DELETE /employees/{id}/)
    """

    # QuerySet - это какие объекты разрешаем видеть
    queryset = Employee.objects.all().order_by("-created_at")

    # Сериализатор, который будет использоваться
    serializer_class = EmployeeSerializer

    # Подключаем DRF SearchFilter
    filter_backends = [SearchFilter]

    # Поля, по которым разрешён поиск
    search_fields = ["full_name", "position", "email"]
