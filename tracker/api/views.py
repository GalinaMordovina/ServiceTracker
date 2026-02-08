from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from tracker.models import Employee, Task
from tracker.api.serializers import EmployeeSerializer, TaskSerializer


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
    filter_backends = [SearchFilter, OrderingFilter]

    # Поля, по которым разрешён поиск
    search_fields = ["full_name", "position", "email"]

    # Сортировака
    ordering_fields = ["created_at", "full_name", "position", "is_active"]
    ordering = ["-created_at"]


class TaskViewSet(ModelViewSet):
    """
    CRUD API для задач.
    """

    # QuerySet - это какие объекты разрешаем видеть
    queryset = Task.objects.all().order_by("-created_at")
    # Сериализатор, который будет использоваться
    serializer_class = TaskSerializer

    # Фильтрация, поиск, сортировка
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Минимальные фильтры
    filterset_fields = ["status", "assignee", "owner"]

    # Поиск
    search_fields = ["title", "description"]

    # Сортировка
    ordering_fields = ["created_at", "due_date", "status"]
    ordering = ["-created_at"]
