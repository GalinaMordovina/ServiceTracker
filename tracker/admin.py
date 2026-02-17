from django.contrib import admin
from tracker.models import Employee, Task, TaskDependency


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # Колонки в списке сотрудников
    list_display = ("id", "full_name", "position", "email", "is_active", "created_at")
    # Поиск по полям
    search_fields = ("full_name", "position", "email")
    # Фильтры справа
    list_filter = ("is_active", "position")
    # Сортировка по умолчанию
    ordering = ("-created_at",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "assignee", "status", "due_date", "created_at")
    search_fields = ("title", "description")
    list_filter = ("status", "due_date", "assignee")
    ordering = ("-created_at",)

    # Удобно выбирать исполнителя, если сотрудников много
    autocomplete_fields = ("assignee",)


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ("id", "parent_task", "child_task")
    search_fields = ("parent_task__title", "child_task__title")
    autocomplete_fields = ("parent_task", "child_task")
