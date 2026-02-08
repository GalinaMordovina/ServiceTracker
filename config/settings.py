from pathlib import Path
import os

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
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}
