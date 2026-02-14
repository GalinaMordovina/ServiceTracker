from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import action  # создать кастомный URL
from rest_framework.response import Response  # вернуть JSON корректно
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import SAFE_METHODS
from drf_spectacular.utils import extend_schema

from tracker.api.permissions import IsAdminOrManager, IsAdminGroup
from tracker.models import Employee, Task
from tracker.api.analytics import (
    get_busy_employees,
    get_important_tasks_with_suggestion,
)
from tracker.api.serializers import (
    EmployeeSerializer,
    TaskSerializer,
    BusyEmployeeSerializer,
    ImportantTaskSerializer,
)


class EmployeeViewSet(ModelViewSet):
    """
    ViewSet для CRUD-операций с сотрудниками.
    По правилам ролей: доступ только для Admin.
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

    def get_permissions(self):
        # Любые действия с сотрудниками разрешены только Admin
        return [IsAdminGroup()]


class TaskViewSet(ModelViewSet):
    """
    CRUD API для задач.
    Роли:
    - чтение (GET, HEAD, OPTIONS) любому аутентифицированному пользователю (Admin/Manager/Employee)
    - изменение (POST/PUT/PATCH/DELETE) только Admin или Manager
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

    def get_permissions(self):
        # SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
        # Чтение разрешаем всем, кто прошёл IsAuthenticated (он в settings)
        if self.request.method in SAFE_METHODS:
            return super().get_permissions()

        # Любые изменения только Admin/Manager
        return [IsAdminOrManager()]


class AnalyticsViewSet(ViewSet):
    """
    Аналитические эндпоинты проекта.
    Только чтение (GET).
    По правилам ролей: доступ только Admin/Manager.
    """

    def get_permissions(self):
        # Аналитика доступна только Admin/Manager
        return [IsAdminOrManager()]

    @extend_schema(
        summary="Занятые сотрудники",
        description=(
                "Возвращает список активных сотрудников с количеством активных задач и списком этих задач. "
                "Список отсортирован по количеству активных задач по убыванию."
        ),
        responses={200: BusyEmployeeSerializer(many=True)},
    )

    @action(detail=False, methods=["get"], url_path="busy-employees")
    def busy_employees(self, request):
        """
        Возвращает список занятых сотрудников с количеством и списком активных задач.
        """
        data = get_busy_employees()  # возвращает list[dict]

        serializer = BusyEmployeeSerializer(data, many=True)
        return Response(serializer.data)  # (режим ввода)

    @extend_schema(
        summary="Важные задачи",
        description=(
                "Возвращает список важных задач и рекомендованного сотрудника для каждой задачи. "
                "Рекомендация может быть пустой (null), если подходящий сотрудник не найден."
        ),
        responses={200: ImportantTaskSerializer(many=True)},
    )

    @action(detail=False, methods=["get"], url_path="important-tasks")
    def important_tasks(self, request):
        """
        Возвращает важные задачи + рекомендуемого сотрудника.
        """
        data = get_important_tasks_with_suggestion()
        serializer = ImportantTaskSerializer(data, many=True)
        return Response(serializer.data)
