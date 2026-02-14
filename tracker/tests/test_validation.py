import pytest
from django.core.exceptions import ValidationError
from tracker.models import Task

pytestmark = pytest.mark.django_db  # - это "глобальная метка" для всего файла.


def test_done_without_report_file_raises_validation_error(task_base):
    """
    По логике: DONE требует report_file.
    task_base из фикстуры уже валиден, мы меняем статус на DONE и ждём ошибку.
    """
    task_base.status = Task.Status.DONE  # Меняем статус на DONE (теперь отчёт обязателен)
    task_base.report_file = None          # Явно обнуляем report_file (чтобы нарушить правило)

    # Ожидаем исключение
    with pytest.raises(ValidationError):
        task_base.full_clean()


def test_owner_equals_assignee_raises_validation_error(emp_owner, valid_due_date):
    """
    По логике: owner не может быть assignee.
    Создаём объект Task (но не сохраняем его),
    и вызываем full_clean(), чтобы проверить валидацию модели.
    """

    # Создаём задачу с одинаковыми owner и assignee
    task = Task(
        title="Bad task",
        description="desc",
        status=Task.Status.NEW,
        owner=emp_owner,
        assignee=emp_owner,
        due_date=valid_due_date,
    )
    # Нам достаточно проверить логику валидации, а не сохранение в БД
    with pytest.raises(ValidationError):
        task.full_clean()
