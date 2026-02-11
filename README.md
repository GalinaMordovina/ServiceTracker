## Трекер задач сотрудников

### Описание:
Сделана ветка аналитики + проверка эндпоинтов в Postman.

#### Что реализовано:

- Добавлены аналитические эндпоинты:

    - `GET /api/analytics/busy-employees/` - сотрудники с активными задачами (`IN_PROGRESS/REVIEW`), сортировка по количеству активных задач (по убыванию), в ответе список задач.

    - `GET /api/analytics/important-tasks/` - задачи со статусом `NEW`, от которых зависит хотя бы одна активная задача через `TaskDependency`.

- Добавлен подбор рекомендуемого сотрудника:

    - кандидат с минимальной нагрузкой (мин. число активных задач)

    - либо исполнитель зависимой активной задачи, если его нагрузка <= min_load + 2

- Добавлены аналитические сериализаторы:

    - `TaskShortSerializer`, `BusyEmployeeSerializer`, `ImportantTaskSerializer`

- Вынесена бизнес-логика аналитики в отдельный модуль `api/analytics.py` (чтобы `views.py` был “тонким”)

### Проверка:
- эндпоинты CRUD (`employees/tasks`) работают
- `analytics` эндпоинты возвращают 200 OK и корректную структуру ответа

### Мини-чеклист Postman
#### Employees

- `GET /api/employees/`
- `POST /api/employees/`
- `PATCH /api/employees/{id}/`
- `DELETE /api/employees/{id}/`
- негативный кейс: `PATCH с { "email": null, "is_active": true }` = 400

#### Tasks

- `GET /api/tasks/`
- фильтры: `?status=NEW`, `?assignee=2`, `?owner=4`
- поиск: `?search=отчет`
- сортировка: `?ordering=due_date`, `?ordering=-created_at`

#### Analytics

- `GET /api/analytics/busy-employees/`
- `GET /api/analytics/important-tasks/`
