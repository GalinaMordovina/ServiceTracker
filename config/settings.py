from pathlib import Path
import os
from datetime import timedelta

from dotenv import load_dotenv


# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent
# Загружаем переменные окружения из файла .env
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv('SECRET_KEY')

# Режим отладки:
DEBUG = os.getenv("DEBUG", "False") == "True"

# Список разрешённых хостов
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# Установленные приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # сторонние
    "rest_framework",
    "django_filters",
    "drf_spectacular",

    # наши приложения
    "tracker",
]

# Middleware (промежуточные слои)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Основной файл маршрутизации
ROOT_URLCONF = 'config.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Точка входа WSGI
WSGI_APPLICATION = 'config.wsgi.application'


# База данных
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",  # Движок базы данных
        "NAME": os.getenv("POSTGRES_DB"),  # Имя базы данных
        "USER": os.getenv("POSTGRES_USER"),  # Пользователь
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),  # Пароль пользователя
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}


# Валидация паролей
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Локализация
LANGUAGE_CODE = 'ru'         # язык интерфейса

TIME_ZONE = 'Europe/Moscow'  # часовой пояс

USE_I18N = True

USE_TZ = True


# Статические и медиа-файлы
STATIC_URL = 'static/'

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Это настройка Django, которая определяет тип поля первичного ключа (id),
# создаваемого по умолчанию для всех моделей, если я явно не указала id в модели.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Настройки Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",                   # отдаёт ответы в JSON
        "rest_framework.renderers.BrowsableAPIRenderer",           # включает красивую HTML-страницу DRF
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",  # подключает генерацию схемы
    "DEFAULT_AUTHENTICATION_CLASSES": (                            # JWT авторизация (Bearer token)
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [                                 # доступ только авторизованным
        "rest_framework.permissions.IsAuthenticated",
    ],
    # когда происходит ошибка, то вызывай функцию custom_exception_handler
    "EXCEPTION_HANDLER": "tracker.api.exceptions.custom_exception_handler",

}

# Настройки drf-spectacular
SPECTACULAR_SETTINGS = {

    # Название API (отображается в Swagger и ReDoc вверху страницы)
    "TITLE": "ServiceTracker API",

    # Краткое описание проекта (что это за API)
    "DESCRIPTION": "Автодокументация API (employees, tasks, analytics, auth)",

    # Версия API (можно менять при развитии проекта)
    "VERSION": "1.0.0",

    # Описание схемы безопасности для Swagger (используем Bearer JWT токены)
    "SECURITY_SCHEMES": {
        "BearerAuth": {
            "type": "http",            # тип авторизации HTTP
            "scheme": "bearer",        # схема Bearer
            "bearerFormat": "JWT",     # формат токена JWT
        }
    },

    # Кнопка "Authorize"
    "SECURITY": [{"BearerAuth": []}],
}

# Увеличим lifetime для проверки
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# Логирование: Logger -> Handler -> Formatter -> Вывод
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,   # если поставить True,то Django отключит стандартные логгеры
    "formatters": {                      # формат
        "simple": {"format": "%(levelname)s | %(name)s | %(message)s"},
    },
    "handlers": {                        # куда писать лог
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "tracker": {"handlers": ["console"], "level": "INFO", "propagate": False},  # не передавать лог выше в root-логгер
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},  # показывать только WARNING и выше
    },
    "root": {"handlers": ["console"], "level": "WARNING"},  # "запасной" логгер (WARNING и выше)
}
