from django.db.models import Count, Q
from typing import Any, Dict, List, Optional

from tracker.models import Employee, Task, TaskDependency


# Статусы, которые считаем "активными"
active_statuses = [
    Task.Status.IN_PROGRESS,
    Task.Status.REVIEW,
]


def get_busy_employees() -> list[dict]:
    """
    Возвращает список сотрудников с активными задачами.
    Для каждого сотрудника (id, full_name, количество активных задач, список активных задач)
    Сотрудники отсортированы по количеству активных задач (по убыванию).
    """

    # 1. Получаем сотрудников и считаем количество активных задач
    employees = (
        Employee.objects
        .filter(is_active=True)
        .annotate(
            active_tasks_count=Count(
                "tasks",                            # related_name из Task.assignee
                filter=Q(tasks__status__in=active_statuses)
            )
        )
        .order_by("-active_tasks_count", "id")
    )

    # 2. Получаем все активные задачи одним запросом
    active_tasks = (
        Task.objects
        .filter(
            status__in=active_statuses,
            assignee__in=employees,
        )
        .select_related("assignee")
    )

    # 3. Группируем задачи по сотрудникам (assignee_id)
    tasks_by_employee: dict[int, list[Task]] = {}

    for task in active_tasks:
        tasks_by_employee.setdefault(task.assignee_id, []).append(task)

    # 4. Формируем результат для сериализатора
    result: list[dict] = []

    for employee in employees:
        # Берём активные задачи сотрудника
        employee_tasks = tasks_by_employee.get(employee.id, [])

        # Если у сотрудника нет активных задач, то пропускаем
        if not employee_tasks:
            continue

        result.append({
            "id": employee.id,
            "full_name": employee.full_name,
            "active_tasks_count": employee.active_tasks_count,
            "active_tasks": employee_tasks,
        })

    return result


def get_important_tasks():
    """
    "Важные задачи" (parent_task):
    1) сами ещё не начаты (status=NEW)
    2) от них зависит хотя бы одна активная задача (child_task со статусом IN_PROGRESS/REVIEW)
    Возвращаем QuerySet Task (parent_task), отсортированный по сроку и созданию.
    """

    # Ищем зависимости, где дочерняя задача активная
    deps = TaskDependency.objects.filter(child_task__status__in=active_statuses)

    # Берём родительские задачи этих зависимостей и фильтруем их по статусу NEW
    important_tasks = (
        Task.objects.filter(
            status=Task.Status.NEW,
            child_dependencies__in=deps,  # child_dependencies - related_name у parent_task
        )
        .distinct()
        .order_by("due_date", "created_at")
    )

    return important_tasks


def get_active_load_by_employee() -> Dict[int, int]:
    """
    Возвращает словарь:
    {employee_id: active_tasks_count(количество задач сотрудника в активном статусе)}
    """
    qs = (
        Employee.objects
        .filter(is_active=True)
        .annotate(
            active_tasks_count=Count(
                "tasks",
                filter=Q(tasks__status__in=active_statuses),
            )
        )
        .values("id", "active_tasks_count")
    )

    return {row["id"]: row["active_tasks_count"] for row in qs}


def get_important_tasks_with_suggestion() -> List[Dict[str, Any]]:
    """
    Важные задачи = родительская задача (от них зависит хотя бы одна активная задача) в статусе NEW

    Для каждой важной задачи выбираем suggested_employee:
    - базовый кандидат: сотрудник с минимальной нагрузкой (min активных задач)
    - альтернативный кандидат: исполнитель дочерней активной задачи, если его нагрузка <= min_load + 2

    Возвращаем список словарей под ImportantTaskSerializer:
    {id, title, due_date, suggested_employee_id, suggested_employee_full_name}
    """

    load_by_employee = get_active_load_by_employee()

    # Если сотрудников нет,то вернем просто список важных задач без рекомендаций
    if not load_by_employee:
        min_load = 0
        min_load_employee_id = None
    else:
        min_load = min(load_by_employee.values())
        min_load_employee_id = min(load_by_employee, key=load_by_employee.get)

    # Загружаем сразу всех активных сотрудников одним запросом
    employee_names: Dict[int, str] = dict(
        Employee.objects
        .filter(is_active=True)
        .values_list("id", "full_name")
    )

    important_qs = (
        Task.objects
        .filter(
            status=Task.Status.NEW,
            child_dependencies__child_task__status__in=active_statuses,
        )
        .distinct()
        .order_by("due_date", "created_at")
        .prefetch_related("child_dependencies__child_task__assignee")
    )

    results: List[Dict[str, Any]] = []

    for task in important_qs:
        suggested_employee_id: Optional[int] = min_load_employee_id

        # кандидат = assignee первой найденной активной дочерней задачи
        child_assignee_id: Optional[int] = None
        for dep in task.child_dependencies.all():
            child_task = dep.child_task
            if child_task.status in active_statuses and child_task.assignee_id:
                child_assignee_id = child_task.assignee_id
                break

        # если у кандидата нагрузка <= min_load + 2 то рекомендуем его
        if child_assignee_id is not None:
            child_load = load_by_employee.get(child_assignee_id, 0)
            if child_load <= min_load + 2:
                suggested_employee_id = child_assignee_id

        # ФИО кандидата из заранее подготовленного словаря
        suggested_full_name = (
            employee_names.get(suggested_employee_id)
            if suggested_employee_id is not None
            else None
        )

        # КЛЮЧИ должны совпадать с ImportantTaskSerializer
        results.append(
            {
                "id": task.id,
                "title": task.title,
                "due_date": task.due_date,
                "suggested_employee_id": suggested_employee_id,
                "suggested_employee_full_name": suggested_full_name,
            }
        )

    return results
