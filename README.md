# ServiceTracker
## Серверное REST-приложение для управления задачами сотрудников
### Описание проекта

ServiceTracker - это серверное приложение, реализованное в формате REST API для управления задачами сотрудников.

### Проект разработан с использованием:
- Python 3.12
- Django 6
- Django REST Framework
- PostgreSQL 17
- JWT-аутентификации
- drf-spectacular (OpenAPI)
- pytest
- Docker

### Приложение поддерживает:
- управление сотрудниками и задачами
- систему зависимостей задач
- аналитику загрузки сотрудников
- интеллектуальный подбор исполнителя
- разграничение прав доступа
- единый формат ошибок
- логирование
- автодокументацию API
- контейнеризацию

### Архитектура проекта

Проект построен по модульному принципу:
```
config/          # настройки проекта
tracker/
    models.py
    api/
        serializers.py
        views.py
        permissions.py
        analytics.py
        exceptions.py
    admin.py
    urls.py
tests/
Dockerfile
docker-compose.yml
```
### Структура базы данных
- Employee (Сотрудник)
  - full_name 
  - position 
  - email 
  - is_active 
  - created_at

- Task (Задача)
  - title 
  - description 
  - owner (FK -> Employee)
  - assignee (FK -> Employee)
  - status (NEW / IN_PROGRESS / REVIEW / DONE)
  - due_date 
  - report_file 
  - review_comment 
  - created_at

Ограничения: owner ≠ assignee, отчет обязателен для DONE, отчет разрешён только для DONE/REVIEW

- TaskDependency (Зависимость задач)
  - parent_task 
  - child_task

Ограничения: уникальность связи, запрет зависимости задачи от самой себя

### Система ролей и доступа

Роли реализованы через Django Groups.

| Роль     | Доступ                 |
| -------- | ---------------------- |
| Admin    | полный CRUD            |
| Manager  | CRUD задач + аналитика |
| Employee | только чтение задач    |

Авторизация реализована через JWT (SimpleJWT).

Получение токена:
```
POST /api/auth/token/
```
Обновление токена:
```
POST /api/auth/token/refresh/
```
### CRUD API
#### Сотрудники
```
/api/employees/
```
Поддерживаются операции:
 - GET
 - POST
 - PUT
 - PATCH
 - DELETE

(доступ только Admin)

#### Задачи
```
/api/tasks/
```
- Чтение - все авторизованные
- Изменение - Admin и Manager

Поддерживаются фильтрация, поиск и сортировка.

### Специальные аналитические эндпоинты
#### 1. Занятые сотрудники
```
GET /api/analytics/busy-employees/
```
Возвращает:
- сотрудника
- количество активных задач
- список активных задач

Сортировка по количеству задач (по убыванию).
#### 2. Важные задачи
```
GET /api/analytics/important-tasks/

```
Определяются как:
- задачи со статусом NEW
- от которых зависят активные задачи

Реализована логика подбора исполнителя:
- наименее загруженный сотрудник
- либо исполнитель зависимой задачи (если его нагрузка ≤ min + 2)

Формат ответа:
```
{
  "id": 10,
  "title": "Ключевая задача",
  "due_date": "2026-02-10",
  "suggested_employee_id": 3,
  "suggested_employee_full_name": "Иванов Иван"
}
```
### Документация API

Автоматическая генерация схемы через `drf-spectacular`.

Swagger:
```
/api/docs/swagger/
```
ReDoc:
```
/api/docs/redoc/
```
Поддерживается авторизация через Bearer JWT.

OpenAPI JSON:
```
/api/schema/
```
### Единый формат ошибок

Все ошибки API возвращаются в едином формате:
```
{
  "status": "error",
  "code": 400,
  "message": "Validation error",
  "errors": {
    "field": "Описание ошибки"
  }
}
```
Обрабатываются:
- 400
- 401
- 403
- 404
- 500

### Логирование

Настроено централизованное логирование.

Используется стандартный модуль `logging`.

Уровни:
- INFO
- WARNING
- ERROR
- EXCEPTION

Логи выводятся в консоль (удобно для Docker logs).

### Тестирование

Используется:
- pytest
- pytest-django

Покрытие ≥ 75%

Запуск:
```
python -m pytest -q
```
Проверка покрытия:
```
python -m pytest --cov=tracker
```

### Контейнеризация (основной способ запуска)

Проект полностью контейнеризирован.

Используются:
- Docker
- docker-compose
- PostgreSQL (отдельный контейнер)
- Gunicorn
- WhiteNoise

#### Запуск через Docker
1. Клонировать репозиторий
```
https://github.com/GalinaMordovina/ServiceTracker.git
cd ServiceTracker
```
2. Создать файл окружения
```
cp .env.example .env
```
3. Запустить
```
docker compose up --build
```
Миграции применяются автоматически.

4. Создать суперпользователя
```
docker compose exec web python manage.py createsuperuser
```

### Доступные URL (после запуска Docker)

По умолчанию сервис доступен на:

- http://localhost:8000/admin/
- http://localhost:8000/api/
- http://localhost:8000/api/docs/swagger/
- http://localhost:8000/api/analytics/busy-employees/


### Альтернативный запуск (без Docker)
```
python -m venv venv
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```
### Архитектурные решения
- REST API - универсальность и масштабируемость
- JWT - stateless авторизация
- PostgreSQL - надежная реляционная СУБД
- DRF ViewSet - минимизация дублирования кода
- drf-spectacular - автодокументация
- кастомный exception handler - единый формат ошибок
- Docker - переносимость и изоляция окружения

## Итог

### Проект реализует:

- управление сотрудниками и задачами
- аналитическую обработку данных
- разграничение прав доступа
- единый формат API
- тестирование
- контейнеризацию

Система готова к развёртыванию и дальнейшему масштабированию.

### Выполнила:

Galina Mordovina (glukoloid@gmail.com) группа 91.0