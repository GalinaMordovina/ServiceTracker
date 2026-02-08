from rest_framework import serializers
from tracker.models import Employee


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
                if "email" is None:
                    email = self.instance.email
                if "is_active" is None:
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
