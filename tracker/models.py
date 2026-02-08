from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F   # Q - логические условия AND, OR, NOT
                                    # F - ссылается на значение другого поля в этой же строке БД

class Employee(models.Model):
    """
    Модель сотрудника (employees).
    Хранит основную информацию об исполнителе задач.
    """

    full_name = models.CharField(
        max_length=255,
        verbose_name="ФИО сотрудника",
    )
    position = models.CharField(
        max_length=255,
        verbose_name="Должность",
    )

    # Опциональные поля:
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )

    # Время создания записи (ставится автоматически при создании)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        db_table = "employees"  # имя таблицы в PostgreSQL
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self) -> str:
        return self.full_name


class Task(models.Model):
    """
    Модель задачи (tasks).
    Используется для хранения информации о задачах сотрудников.
    """

    # Ограничиваем значения статуса только разрешёнными вариантами
    class Status(models.TextChoices):
        NEW = "NEW", "Новая"
        IN_PROGRESS = "IN_PROGRESS", "В работе"
        REVIEW = "REVIEW", "На проверке"
        DONE = "DONE", "Завершена"

    title = models.CharField(
        max_length=255,
        verbose_name="Название задачи",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание задачи",
    )
    report_file = models.FileField(
        upload_to="task_reports/",
        blank=True,
        null=True,
        verbose_name="Отчёт/документ",
    )
    review_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий проверяющего",
    )
    assignee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,  # если сотрудника удалили у задачи assignee станет NULL
        null=True,                  # assignee может быть NULL (если задача ещё не назначена)
        blank=True,
        related_name="tasks",       # employee.tasks.all()
        verbose_name="Исполнитель",
    )
    owner = models.ForeignKey(
        "Employee",
        on_delete=models.PROTECT,
        related_name="owned_tasks",
        verbose_name="Владелец задачи",
        null=True,                  # временно разрешаем NULL
        blank=True,                 # временно разрешаем пустое значение в формах/админке
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус задачи",
    )
    due_date = models.DateField(
        verbose_name="Срок выполнения",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    def clean(self) -> None:
        """
        Бизнес-валидация задачи.
        Отчёт (report_file) разрешён только для статусов DONE и REVIEW (для статуса DONE отчет обязателен).
        Владелец задачи (owner) не может быть её исполнителем (assignee).
        """
        allowed_statuses = {self.Status.DONE, self.Status.REVIEW}

        # 1) Если отчёт прикреплён, статус должен быть DONE или REVIEW
        if self.report_file and self.status not in allowed_statuses:
            raise ValidationError(
                {"report_file": "Отчёт можно прикреплять только для задач со статусом DONE или REVIEW."}
            )

        # 2) Если статус DONE отчёт обязателен
        if self.status == self.Status.DONE and not self.report_file:
            raise ValidationError(
                {"report_file": "Для статуса DONE необходимо прикрепить отчёт."}
            )
        # (owner != assignee) self.owner и self.assignee - это ORM-объекты - добавить _id?
        if self.assignee is not None and self.owner == self.assignee:
            raise ValidationError({"assignee": "Владелец задачи не может быть её исполнителем."})

    def save(self, *args, **kwargs):
        # Запускает:
        # - clean_fields()
        # - clean()
        # - validate_unique()
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "tasks"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

        constraints = [
            # Запрет: владелец задачи не может быть её исполнителем
            models.CheckConstraint(
                condition=Q(assignee__isnull=True) | ~Q(owner=F("assignee")),
                name="prevent_owner_is_assignee",
            ),
        ]

        # Индексы ускоряют фильтры в API (assignee/status/due_date)
        indexes = [
            models.Index(fields=["status"], name="idx_tasks_status"),
            models.Index(fields=["due_date"], name="idx_tasks_due_date"),
            models.Index(fields=["assignee", "status"], name="idx_tasks_assignee_status"),
        ]

    def __str__(self) -> str:
        return self.title


class TaskDependency(models.Model):
    """
    Модель зависимости задач (task_dependencies).
    Описывает связь: родительская задача -> дочерняя задача.
    """

    parent_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="child_dependencies",
        verbose_name="Родительская задача",
    )
    child_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="parent_dependencies",
        verbose_name="Дочерняя задача",
    )

    class Meta:
        db_table = "task_dependencies"
        verbose_name = "Зависимость задачи"
        verbose_name_plural = "Зависимости задач"
        constraints = [
            # Запрет дублирования связей
            models.UniqueConstraint(
                fields=["parent_task", "child_task"],
                name="unique_task_dependency",
            ),
            # Запрет зависимости задачи от самой себя
            models.CheckConstraint(
                condition=~Q(parent_task=F("child_task")),
                name="prevent_self_dependency",
            ),
        ]
    # возвращаю объекты, а не id (возможно поменяю)
    def __str__(self) -> str:
        return f"{self.parent_task} -> {self.child_task}"
