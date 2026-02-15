## Трекер задач сотрудников

### Что сделано в ветке logging-and-errors

### 1) Единый формат ошибок API
Подключён кастомный обработчик исключений DRF:

- `tracker/api/exceptions.py`
- `REST_FRAMEWORK["EXCEPTION_HANDLER"] = "tracker.api.exceptions.custom_exception_handler"`

Теперь ошибки возвращаются в едином JSON-формате, например:

**401 (нет JWT токена)**
```json
{
  "status": "error",
  "code": 401,
  "message": "Authentication required"
}
```
**403 (нет прав)**
```
{
  "status": "error",
  "code": 403,
  "message": "Permission denied"
}
```
**500 (необработанная ошибка)**
```
{
  "status": "error",
  "code": 500,
  "message": "Internal server error"
}
```
### 2) Минимальное логирование в консоль

Настроен `LOGGING` в `settings.py` для вывода в консоль (stdout).

Логи помогают быстро понять:

- какой URL вызвали
- какой метод
- какой статус
- какой тип ошибки

Пример логов при проверке 401:
```
WARNING | tracker | API GET /api/analytics/busy-employees/ -> 401 (NotAuthenticated)
WARNING | django.request | Unauthorized: /api/analytics/busy-employees/
```
Пример логов при неверных учётных данных на JWT token endpoint:
```
WARNING | tracker | API POST /api/auth/token/ -> 401 (AuthenticationFailed)
WARNING | django.request | Unauthorized: /api/auth/token/
```

### Проверка

- 401: вызвать /api/analytics/busy-employees/ без токена
- 403: вызвать /api/analytics/busy-employees/ с токеном пользователя без ролей Admin/Manager
- убедиться, что ответ в JSON единого формата и что логи появляются в консоли

## Проверка качества кода

Перед завершением ветки выполнены следующие проверки:

### 3) Тестирование

```bash
python -m pytest --cov=tracker
```

Результат:
- Все тесты проходят
- Требование ≥ 75% выполнено

### 4) Проверка PEP8
`flake8 .`

Используется конфигурация:
- max-line-length = 150
- игнорируется правило E116 (стиль выравнивания многострочных конструкций)
- исключены папки `migrations`, `pycache`, `.venv`

Ошибок линтера нет.

### Дополнение: 
Особенность JWT token endpoint

Эндпоинт `/api/auth/token/` (SimpleJWT) при неверных учётных данных
возвращает:

```json
{
  "status": "error",
  "code": 401,
  "message": "API error"
}
```
Это связано с тем, что исключение `AuthenticationFailed`
обрабатывается общим блоком кастомного exception handler.

Текущая реализация соответствует единому формату ошибок,
однако сообщение можно сделать более конкретным
(например, "Invalid credentials").

На данном этапе проекта поведение оставлено без изменений.
При необходимости сообщение может быть уточнено
добавлением отдельной обработки `AuthenticationFailed`.
