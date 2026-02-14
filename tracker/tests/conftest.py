import pytest
from datetime import date, timedelta

from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tracker.models import Employee, Task


@pytest.fixture()
def api_client() -> APIClient:
    """
    DRF-клиент для запросов к API.
    Его используем в тестах: api_client.get/post/patch...
    """
    return APIClient()


def _access_token(user) -> str:
    """
    Генерируем JWT access token для пользователя.
    (не ходим в /api/auth/token/, чтобы тесты быстрее и стабильнее)
    """
    refresh = RefreshToken.for_user(user)   # создаём refresh-токен для пользователя
    return str(refresh.access_token)        # вытаскиваем access-токен и приводим к строке


@pytest.fixture()
def groups(db):
    """
    Создаём группы ролей, которые используются в permissions:
    Admin, Manager, Employee
    """
    admin, _ = Group.objects.get_or_create(name="Admin")
    manager, _ = Group.objects.get_or_create(name="Manager")
    employee, _ = Group.objects.get_or_create(name="Employee")

    # Возвращаем словарь, чтобы удобно брать по ключу: groups["Admin"]
    return {"Admin": admin, "Manager": manager, "Employee": employee}


@pytest.fixture()
def admin_user(django_user_model, groups):
    """
    Создаём Django-пользователя и добавляем его в группу Admin.
    """
    user = django_user_model.objects.create_user(username="admin", password="pass12345")
    user.groups.add(groups["Admin"])    # назначаем роль Admin через группу
    return user


@pytest.fixture()
def manager_user(django_user_model, groups):
    """
    Пользователь с ролью Manager.
    """
    user = django_user_model.objects.create_user(username="manager", password="pass12345")
    user.groups.add(groups["Manager"])
    return user


@pytest.fixture()
def employee_user(django_user_model, groups):
    """
    Пользователь с ролью Employee.
    """
    user = django_user_model.objects.create_user(username="employee", password="pass12345")
    user.groups.add(groups["Employee"])
    return user


@pytest.fixture()
def admin_token(admin_user) -> str:         # JWT access token для admin_user
    return _access_token(admin_user)


@pytest.fixture()
def manager_token(manager_user) -> str:     # JWT access token для manager_user
    return _access_token(manager_user)


@pytest.fixture()
def employee_token(employee_user) -> str:   # JWT access token для employee_user
    return _access_token(employee_user)


@pytest.fixture()
def auth_client():
    """
    Удобная фабрика клиента возвращает DRF-клиент с заголовком Authorization:
    client = auth_client(manager_token)
    response = client.get("/api/tasks/")
    """
    def _make(token: str) -> APIClient:  # DRF SimpleJWT ожидает токен: Authorization: Bearer <token>
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client
    return _make


# ДАННЫЕ ДОМЕНА (Employee/Task)

@pytest.fixture()
def emp_owner(db) -> Employee:
    """
    Сотрудник-владелец задачи (owner).
    Для API-тестов сотрудников (создание через API) email будем указывать.
    """
    return Employee.objects.create(full_name="Owner One", position="Dev", email="o1@example.com")


@pytest.fixture()
def emp_assignee(db) -> Employee:
    """
    Сотрудник-исполнитель задачи (assignee).
    """
    return Employee.objects.create(full_name="Assignee One", position="QA", email="a1@example.com")


@pytest.fixture()
def valid_due_date() -> date:
    """
    В TaskSerializer стоит правило: due_date не может быть в прошлом.
    Поэтому везде используем дату "завтра".
    """
    return date.today() + timedelta(days=1)


@pytest.fixture()
def task_base(db, emp_owner, emp_assignee, valid_due_date) -> Task:
    """
    Базовая валидная задача (due_date обязателен).
    """
    return Task.objects.create(
        title="Base task",
        description="desc",
        status=Task.Status.NEW,
        owner=emp_owner,
        assignee=emp_assignee,
        due_date=valid_due_date,
    )
