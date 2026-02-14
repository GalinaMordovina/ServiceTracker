## Трекер задач сотрудников

### В рамках данной ветки реализована автогенерация OpenAPI-документации для дипломного проекта ServiceTracker API.

Что сделано:
- Подключена библиотека `drf-spectacular`
- Настроена генерация OpenAPI-схемы
- Добавлены маршруты:
  - /api/schema/ 
  - /api/docs/swagger/ 
  - /api/docs/redoc/

- Настроена JWT Bearer security scheme
- Добавлены @extend_schema для аналитических action’ов:
  - busy-employees 
  - important-tasks
- HealthCheck endpoint исключён из документации как инфраструктурный

Проверено, что:
- JWT продолжает работать
- permissions не изменились
- pytest проходит без ошибок

Проверка:

- Swagger UI: `/api/docs/swagger/`
- ReDoc: `/api/docs/redoc/`
- OpenAPI JSON: `/api/schema/`
