import pytest
from datetime import date, timedelta

from tracker.models import Employee, Task, TaskDependency

pytestmark = pytest.mark.django_db  # - это "глобальная метка" для всего файла.

# URL аналитики (чтобы не дублировать строки)
BUSY_URL = "/api/analytics/busy-employees/"
IMPORTANT_URL = "/api/analytics/important-tasks/"


def _tomorrow():
    """
    Возвращаем дату "завтра".
    есть правило: due_date не может быть в прошлом.
    Task требует due_date (обязательное поле).
    """
    return date.today() + timedelta(days=1)


def test_busy_employees_sorted_by_active_tasks_count(auth_client, manager_token):
    """
    Проверяем:
    - employee_1 имеет 2 активные задачи
    - employee_2 имеет 1 активную задачу
    В ответе /busy-employees/ employee_1 должен идти первым (по active_tasks_count).
    """

    # owner отдельный, чтобы не нарушать правило owner != assignee
    owner = Employee.objects.create(
        full_name="Task Owner",
        position="Lead",
        email="owner@example.com",
        is_active=True,
    )
    # Два исполнителя (assignee)
    e1 = Employee.objects.create(full_name="E One", position="Dev", email="e1@example.com", is_active=True)
    e2 = Employee.objects.create(full_name="E Two", position="QA", email="e2@example.com", is_active=True)

    # 2 активные задачи на e1
    Task.objects.create(
        title="t1", status=Task.Status.IN_PROGRESS,
        owner=owner, assignee=e1, due_date=_tomorrow()
    )
    Task.objects.create(
        title="t2", status=Task.Status.REVIEW,
        owner=owner, assignee=e1, due_date=_tomorrow()
    )
    # 1 активная задача на e2
    Task.objects.create(
        title="t3", status=Task.Status.IN_PROGRESS,
        owner=owner, assignee=e2, due_date=_tomorrow()
    )

    # Авторизуемся как Manager (аналитика доступна Admin/Manager)
    client = auth_client(manager_token)
    # Делаем запрос к /busy-employees/
    resp = client.get(BUSY_URL)
    assert resp.status_code == 200

    # Ответ: список словарей
    data = resp.json()
    assert isinstance(data, list)
    # Должно быть минимум 2 записи, потому что у нас 2 сотрудника с активными задачами
    assert len(data) >= 2

    # Проверяем сортировку и подсчёт
    assert data[0]["id"] == e1.id
    assert data[0]["active_tasks_count"] == 2
    assert data[1]["id"] == e2.id
    assert data[1]["active_tasks_count"] == 1


def test_important_tasks_parent_included(auth_client, manager_token):
    """
    Условие "важной" задачи по analytics.py:
    - parent_task status=NEW
    - есть dependency, где child_task активная (IN_PROGRESS/REVIEW)

    Создаём:
    parent NEW
    child IN_PROGRESS
    связываем dependency parent -> child
    Затем проверяем, что parent попал в /important-tasks/.
    """

    # Отдельный владелец и отдельный исполнитель:
    owner = Employee.objects.create(
        full_name="Task Owner",
        position="Lead",
        email="owner2@example.com",
        is_active=True,
    )
    assignee = Employee.objects.create(
        full_name="Worker",
        position="Dev",
        email="worker@example.com",
        is_active=True,
    )

    # Родительская задача: NEW (не начата)
    parent = Task.objects.create(
        title="parent", status=Task.Status.NEW,
        owner=owner, assignee=assignee, due_date=_tomorrow()
    )
    # Дочерняя задача: активная (IN_PROGRESS)
    child = Task.objects.create(
        title="child", status=Task.Status.IN_PROGRESS,
        owner=owner, assignee=assignee, due_date=_tomorrow()
    )

    # Создаём зависимость: parent -> child
    TaskDependency.objects.create(parent_task=parent, child_task=child)

    # Авторизация как Manager
    client = auth_client(manager_token)
    # Запрос к /important-tasks/
    resp = client.get(IMPORTANT_URL)
    assert resp.status_code == 200

    # Ответ: список "важных задач"
    data = resp.json()
    # Собираем все id из ответа
    ids = [item["id"] for item in data]

    # Проверяем, что родительская задача попала в выдачу
    assert parent.id in ids
