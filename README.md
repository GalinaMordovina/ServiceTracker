## Трекер задач сотрудников

### Тестирование
В проекте реализовано тестирование с использованием:
- pytest
- pytest-django
- pytest-cov

#### Покрытие тестами > 90%

#### Тестируются:
- Права доступа (Admin / Manager / Employee)
- CRUD для задач и сотрудников
- Валидация модели Task
- Аналитические эндпоинты:
  - /api/analytics/busy-employees/ 
  - /api/analytics/important-tasks/

#### Запуск тестов:
```
python -m pytest -q
```
#### Проверка покрытия:
```
python -m pytest --cov=tracker
```
