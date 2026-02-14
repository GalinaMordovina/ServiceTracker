import pytest
from datetime import date, timedelta

pytestmark = pytest.mark.django_db  # - это "глобальная метка" для всего файла.

# URL эндпоинтов, которые тестируем (чтобы не дублировать строки по всему файлу)
TASKS_URL = "/api/tasks/"
EMPLOYEES_URL = "/api/employees/"
BUSY_URL = "/api/analytics/busy-employees/"
IMPORTANT_URL = "/api/analytics/important-tasks/"


def _tomorrow() -> str:
    """
    Возвращаем дату "завтра" в формате строки YYYY-MM-DD.
    (DRF в POST ожидает JSON, а JSON не умеет объект date)
    """
    return (date.today() + timedelta(days=1)).isoformat()


def test_no_token_tasks_list_401(api_client):
    """
    Без токена DRF + JWT должны вернуть 401.
    """
    resp = api_client.get(TASKS_URL)  # неавторизованный запрос
    assert resp.status_code == 401


def test_no_token_analytics_busy_401(api_client):
    """
    Аналитика тоже требует токен => 401.
    """
    resp = api_client.get(BUSY_URL)
    assert resp.status_code == 401


def test_employee_can_get_tasks_200(auth_client, employee_token):
    """
    По правилам: GET /tasks/ доступен любому аутентифицированному.
    """
    client = auth_client(employee_token)  # создаём клиент с заголовком Authorization: Bearer <token>
    resp = client.get(TASKS_URL)          # GET /api/tasks/
    assert resp.status_code == 200


def test_employee_cannot_post_tasks_403(auth_client, employee_token, emp_owner, emp_assignee):
    """
    Employee не может создавать задачи => 403.
    """
    client = auth_client(employee_token)
    payload = {
        "title": "Task from employee",
        "description": "desc",
        "status": "NEW",
        "owner": emp_owner.id,
        "assignee": emp_assignee.id,
        "due_date": _tomorrow(),
    }
    resp = client.post(TASKS_URL, payload, format="json")
    assert resp.status_code == 403  # аутентифицирован, но прав не хватает


def test_employee_cannot_access_busy_403(auth_client, employee_token):
    """
    Аналитика только Admin/Manager => Employee получит 403.
    """
    client = auth_client(employee_token)
    resp = client.get(BUSY_URL)
    assert resp.status_code == 403


def test_manager_can_post_tasks_201(auth_client, manager_token, emp_owner, emp_assignee):
    """
    Manager может создавать задачи => 201.
    """
    client = auth_client(manager_token)
    payload = {
        "title": "Task from manager",
        "description": "desc",
        "status": "NEW",
        "owner": emp_owner.id,
        "assignee": emp_assignee.id,
        "due_date": _tomorrow(),
    }
    resp = client.post(TASKS_URL, payload, format="json")
    assert resp.status_code == 201


def test_manager_can_access_busy_200(auth_client, manager_token):
    """
    Manager имеет доступ к busy-employees => 200.
    """
    client = auth_client(manager_token)
    resp = client.get(BUSY_URL)
    assert resp.status_code == 200


def test_manager_can_access_important_200(auth_client, manager_token):
    """
    Manager имеет доступ к important-tasks => 200.
    """
    client = auth_client(manager_token)
    resp = client.get(IMPORTANT_URL)
    assert resp.status_code == 200


def test_admin_can_create_employee_201(auth_client, admin_token):
    """
    CRUD сотрудников только Admin.
    (по EmployeeSerializer для активного сотрудника email обязателен)
    """
    client = auth_client(admin_token)
    payload = {
        "full_name": "New Employee Person",
        "position": "Designer",
        "email": "new.employee@example.com",
        "is_active": True,
    }
    resp = client.post(EMPLOYEES_URL, payload, format="json")
    assert resp.status_code == 201
