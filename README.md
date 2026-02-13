## Трекер задач сотрудников

### Исправления и улучшения:
1. Устранено дублирование эндпоинта `important-tasks`
Ранее в AnalyticsViewSet было объявлено два метода с одинаковым:
```
@action(detail=False, url_path="important-tasks")
```
В Python второй метод перезаписывал первый, что приводило к скрытому багу.

#### Исправление:
Оставлен один метод `important_tasks` и реализована версия с рекомендацией сотрудника

2. Безопасная обработка nullable owner

Метод `get_owner_full_name()` обновлён:
```
def get_owner_full_name(self, obj):
    return obj.owner.full_name if obj.owner else None
```
Теперь при owner=None сериализация не приводит к AttributeError.

3. Оптимизация функции `get_important_tasks_with_suggestion`
Устранена проблема N+1 запросов.

Ранее внутри цикла выполнялся запрос к БД для каждого task:
```
Employee.objects.filter(id=suggested_employee_id)
```
#### Теперь:
ФИО активных сотрудников загружаются одним запросом и используется словарь id -> full_name
```
employee_names = dict(
    Employee.objects.filter(is_active=True).values_list("id", "full_name")
)
```
Преимущества:
- меньше SQL-запросов
- более масштабируемое решение
- сохранён контракт сериализатора

## Аутентификация и роли

В проекте реализована JWT-аутентификация с разграничением прав доступа по ролям.

Используемые технологии
- djangorestframework-simplejwt
- Django Groups
- кастомные permission classes

Используются три роли:
- Admin (администратор)
- Manager (менеджер)
- Employee (пользователь)

### Admin

Полный доступ к системе:
- CRUD сотрудников ✅ 
- CRUD задач  ✅ 
- Аналитика (busy-employees, important-tasks) ✅ 
- Удаление задач ✅ 

### Manager

Ограниченный управленческий доступ:
- Просмотр сотрудников ✅
- Создание задач ✅ 
- Изменение задач ✅  
- Аналитика ✅ 
 
Запрещено удаление задач ❌

### Employee
Минимальные права:
- Просмотр задач ✅

Запрещено: 
- Создание задач ❌ 
- Изменение задач  ❌ 
- Удаление задач  ❌ 
- Список сотрудников ❌  
- Аналитика ❌
 
### Получение токена:
```
POST /api/auth/token/
```
Тело запроса:
```
{
  "username": "admin_user",
  "password": "admin123"
}
```
Ответ:
```
{
  "refresh": "....",
  "access": "...."
}
```
Использование токена

В каждый защищённый запрос необходимо передавать заголовок:
```
Authorization: Bearer <access_token>
```
