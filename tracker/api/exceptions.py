import logging

from django.http import Http404         # стандартное исключение Django
from rest_framework import status       # Статусы HTTP (200, 400, 500 и т.д.)
from rest_framework.exceptions import (
    NotAuthenticated,   # 401 - пользователь не передал токен
    PermissionDenied,   # 403 - нет прав
    ValidationError,    # 400 - ошибка валидации данных
)

from rest_framework.response import Response
from rest_framework.views import exception_handler


# Получаем логгер с именем "tracker"
logger = logging.getLogger("tracker")


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для DRF.
    Его задача:
    1) Сделать единый формат ошибок в JSON
    2) Логировать ошибки в консоль (или Docker logs)
    3) Не отдавать traceback клиенту при 500
    """

    # Получаем request (чтобы знать какой метод и какой URL вызвал ошибку)
    request = context.get("request")

    # Попробуем обработать ошибку стандартным способом (ValidationError, PermissionDenied и т.д.)
    response = exception_handler(exc, context)

    # Если DRF смог обработать ошибку (например 400/401/403/404)
    if response is not None:
        code = response.status_code  # HTTP статус (400, 403 и т.д.)

        # Формируем единый JSON-формат

        # Ошибка валидации (например неправильный email)
        if isinstance(exc, ValidationError):
            payload = {
                "status": "error",
                "code": code,
                "message": "Validation error",
                "errors": response.data,  # DRF уже вернул структуру ошибок
            }

        # Не передан токен (401)
        elif isinstance(exc, NotAuthenticated):
            payload = {
                "status": "error",
                "code": code,
                "message": "Authentication required",
            }

        # Нет прав (403)
        elif isinstance(exc, PermissionDenied):
            payload = {
                "status": "error",
                "code": code,
                "message": "Permission denied",
            }

        # Объект не найден (404)
        elif isinstance(exc, Http404):
            payload = {
                "status": "error",
                "code": code,
                "message": "Not found",
            }

        # Прочие ошибки DRF
        else:
            payload = {
                "status": "error",
                "code": code,
                "message": "API error",
            }

        # Пишем в лог: метод, URL, код, тип ошибки
        logger.warning(
            "API %s %s -> %s (%s)",
            getattr(request, "method", "-"),  # например GET
            getattr(request, "path", "-"),          # например /api/tasks/
            code,                                   # например 403
            exc.__class__.__name__,                 # например PermissionDenied
        )

        # Подменяем стандартный ответ DRF на наш единый формат
        response.data = payload
        return response

    # Если DRF не смог обработать ошибку = (500)
    logger.exception(
        "API %s %s -> 500 (Unhandled exception)",
        getattr(request, "method", "-"),
        getattr(request, "path", "-"),
    )

    # Отдаём аккуратный JSON
    return Response(
        {
            "status": "error",
            "code": 500,
            "message": "Internal server error",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
