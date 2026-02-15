# 1. Базовый образ
FROM python:3.12-slim

# 2. Рабочая папка внутри контейнера
WORKDIR /app

# 3. Копируем зависимости
COPY requirements.txt /app/

# 4. Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# 5. Копируем весь проект внутрь контейнера
COPY . /app/

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 6. Открываем порт
EXPOSE 8000

# 7. Команда запуска
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
