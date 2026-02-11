from rest_framework import serializers
from tracker.models import Employee, Task


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Employee.
    Отвечает за:
    - преобразование объекта Employee -> JSON
    - проверку входящих данных (JSON -> Python)
    - создание и обновление объектов Employee через .save()
    """

    class Meta:
        # Модель, с которой работает сериализатор
        model = Employee

        # Явно перечисляем поля, которые будут доступны в API
        fields = (
            "id",
            "full_name",
            "position",
            "email",
            "is_active",
            "created_at",
        )

        # Эти поля нельзя передавать в POST/PUT/PATCH (заполняются автоматически моделью)
        read_only_fields = (
            "id",
            "created_at",
        )

    def validate_full_name(self, value: str) -> str:
        """
        Валидация отдельного поля full_name.
        Автоматически вызывается DRF, если full_name присутствует во входных данных.
        """
        value = value.strip()

        if len(value) < 5:
            raise serializers.ValidationError(
                "ФИО слишком короткое. Укажите полное имя."
            )

        return value

    def validate(self, attrs: dict) -> dict:
        """
        Межполевная валидация. Корректно работает для POST/PUT/PATCH.
        Проверяем логические связи между несколькими полями входного запроса.
        """
        email = attrs.get("email")
        is_active = attrs.get("is_active")

        if self.instance is not None:
            # PATCH: берём из instance, если поле не передали
            if self.partial:
                if "email" not in attrs:
                    email = self.instance.email
                if "is_active" not in attrs:
                    is_active = self.instance.is_active
            # PUT: attrs содержит полную модель и ничего не подставляем
        else:
            # POST: если is_active не передали, считаем True
            if is_active is None:
                is_active = True

        if is_active and not email:
            raise serializers.ValidationError(
                {"email": "Для активного сотрудника необходимо указать email."}
            )

        return attrs


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для задач.
    Принимаем FK (assignee/owner) как id, но отдает -> *_full_name.
    """

    assignee_full_name = serializers.SerializerMethodField()
    owner_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "assignee",
            "assignee_full_name",
            "owner",
            "owner_full_name",
            "status",
            "due_date",
            "report_file",
            "review_comment",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "assignee_full_name", "owner_full_name")

    def get_assignee_full_name(self, obj: Task) -> str | None:
        """Возвращаем ФИО исполнителя, если он назначен."""
        return obj.assignee.full_name if obj.assignee else None

    def get_owner_full_name(self, obj: Task) -> str:
        """Владелец задачи обязателен, поэтому None быть не должно."""  # а если будет что делать?
        return obj.owner.full_name

    def validate_due_date(self, value):  # можно отключить/изменить правило
        """
        Пример валидации даты: запрет на прошедшую дату.
        """
        from datetime import date

        if value < date.today():
            raise serializers.ValidationError("Срок выполнения не может быть в прошлом.")
        return value

    def validate(self, attrs: dict) -> dict:  # модель уже защищена clean()+full_clean()
        """
        Межполевная валидация:
        - report_file разрешён только для DONE/REVIEW
        - для DONE report_file обязателен
        - owner не может быть равен assignee
        """
        # Текущие значения из запроса
        status = attrs.get("status")
        report_file = attrs.get("report_file")
        assignee = attrs.get("assignee")
        owner = attrs.get("owner")

        # Для PATCH: если поле не пришло, то берем из instance
        if self.instance is not None:
            if "status" not in attrs:
                status = self.instance.status
            if "report_file" not in attrs:
                report_file = self.instance.report_file
            if "assignee" not in attrs:
                assignee = self.instance.assignee
            if "owner" not in attrs:
                owner = self.instance.owner

        allowed_statuses = {Task.Status.DONE, Task.Status.REVIEW}

        # 1) Если report_file прикреплён, то статус должен быть DONE или REVIEW
        if report_file and status not in allowed_statuses:
            raise serializers.ValidationError(
                {"report_file": "Отчёт можно прикреплять только для задач со статусом DONE или REVIEW."}
            )

        # 2) Если статус DONE, то отчёт обязателен
        if status == Task.Status.DONE and not report_file:
            raise serializers.ValidationError(
                {"report_file": "Для статуса DONE необходимо прикрепить отчёт."}
            )

        # 3) Владелец не может быть исполнителем
        if assignee is not None and owner == assignee:
            raise serializers.ValidationError(
                {"assignee": "Владелец задачи не может быть её исполнителем."}
            )

        return attrs


# Это не ModelSerializer ибо формат ответа "аналитический", а не CRUD
class TaskShortSerializer(serializers.ModelSerializer):
    """
    Короткий сериализатор задачи для аналитики.
    Используется в списке активных задач сотрудника.
    """
    class Meta:
        model = Task
        fields = ("id", "title", "status", "due_date")


class BusyEmployeeSerializer(serializers.Serializer):
    """
    Короткий сериализатор задачи для аналитики "Занятые сотрудники".
    Используется в списке активных задач сотрудника.
    """
    id = serializers.IntegerField()                     # обычное числовое поле (соответствует Employee.id)
    full_name = serializers.CharField()                 # строковое поле (соответствует Employee.full_name)
    active_tasks_count = serializers.IntegerField()     # количество активных задач (вычисляется в analytics.py)
    active_tasks = TaskShortSerializer(many=True)       # список активных задач сотрудника


class ImportantTaskSerializer(serializers.Serializer):
    """
    Сериализатор для выдачи "важных задач" в аналитике.
    Результат: "важная задача" + "рекомендованный сотрудник"
    """

    id = serializers.IntegerField()
    title = serializers.CharField()
    due_date = serializers.DateField()

    # Рекомендованный сотрудник (может быть None, если сотрудников нет или логика не нашла кандидата)
    suggested_employee_id = serializers.IntegerField(allow_null=True)
    suggested_employee_full_name = serializers.CharField(allow_null=True)
