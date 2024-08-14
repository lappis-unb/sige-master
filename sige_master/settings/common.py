from datetime import time
from pathlib import Path

from rich.console import Console

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
LOG_PATH = BASE_DIR / "logs"
APP_DIR = BASE_DIR / "apps"
CSV_DIR_PATH = APP_DIR / "memory_maps" / "csv_maps"


# APPS
# ------------------------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django.utils.translation",
]

EXTERNAL_APPS = [
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "rest_framework",
    "rest_framework_simplejwt",
]

LOCAL_APPS = [
    "apps.accounts",
    "apps.locations",
    "apps.organizations",
    "apps.memory_maps",
    "apps.transductors",
    "apps.measurements",
    "apps.unifilar_diagram",
    "apps.events",
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS


# MIDDLEWARE
# ------------------------------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]


# TEMPLATES
# ------------------------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# PASSWORDS
# ------------------------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation." "UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation." "MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation." "CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation." "NumericPasswordValidator"},
]


# AUTHENTICATION
# ------------------------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# INTERNATIONALIZATION
# ------------------------------------------------------------------------------------------------
TIME_ZONE = "America/Sao_Paulo"

LOCALE_NAME = "pt_br"
LANGUAGE_CODE = "pt-br"
LANGUAGES = (
    ("en-us", "English"),
    ("pt-br", "Português"),
)

LOCALE_PATHS = (BASE_DIR / "locale",)
USE_I18N = True
USE_TZ = True


# GENERAL
# ------------------------------------------------------------------------------------------------
ROOT_URLCONF = "sige_master.urls"
WSGI_APPLICATION = "sige_master.wsgi.application"
AUTH_USER_MODEL = "accounts.Account"

SESSION_LOGIN = True
USE_JWT = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

APPEND_SLASH = True
LOGIN_REDIRECT_URL = "/"




# TIME SETTINGS
# ------------------------------------------------------------------------------------------------
# Coletas de 15 min são registradas no fim; registros até XX:00:59 vêm do intervalo anterior.
# Ex: 18:00:** cobre 17:45-17:59 (fora de pico); 21:00:** cobre 20:45-20:59 (pico).

PEAK_TIME_START = time(18, 00, 59)
PEAK_TIME_END = time(21, 00, 59)
INTERMEDIATE_TIME_START = time(17, 00, 59)
INTERMEDIATE_TIME_END = time(22, 00, 59)
OFF_PEAK_TIME_START = time(22, 00, 59)
OFF_PEAK_TIME_END = time(18, 00, 59)


# DJANGO REST FRAMEWORK
# ------------------------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny"
        # "rest_framework.permissions.IsAuthenticated",
        # 'rest_framework.permissions.DjangoModelPermissions',
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}


# LOGGING
# ------------------------------------------------------------------------------------------------
# Config Console RichHandler
console = Console(width=130, no_color=False)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rich": {
            "format": "%(threadName)s - %(message)s",
            "datefmt": "[%X]",
        },
        "simple": {
            "format": "%(levelname)-8s: %(message)s",
        },
        "middle": {
            "format": "%(module)-12s: [line: %(lineno)-3s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "verbose": {
            "format": "%(asctime)-15s | %(levelname)-8s | %(filename)-15s | line:%(lineno)-3s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(server_time)s] %(message)s",
        },
    },
    # "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
    "handlers": {
        "django.server": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "rich-console": {
            "class": "rich.logging.RichHandler",
            "console": console,
            "formatter": "rich",
            "level": "DEBUG",
            "rich_tracebacks": True,
            "show_time": True,
            "show_path": True,
            "show_level": False,
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "tasks-file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_PATH / "tasks" / "tasks.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,  # 5 files = 50MB total
            "formatter": "verbose",
        },
        "apps-file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_PATH / "apps" / "apps.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,  # 5 files = 50MB total
            "formatter": "verbose",
        },
        "error_file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": LOG_PATH / "erros.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {"handlers": ["error_file"], "propagate": True},
        "": {"handlers": ["error_file"], "level": "INFO", "propagate": True},  # root logger
        "django.server": {"handlers": ["django.server"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["error_file"], "level": "ERROR", "propagate": False},
        "django.db.backends": {"handlers": ["console"], "level": "INFO"},
        "tasks": {"handlers": ["tasks-file", "rich-console"], "level": "DEBUG", "propagate": False},
        "apps": {"handlers": ["apps-file", "rich-console"], "level": "DEBUG", "propagate": False},
    },
}


# SPECTACULAR SETTINGS
# ---------------------------------------------------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "SIGE API - Energy Management System",
    "DESCRIPTION": " API for collecting and managing data from the energy monitoring system",
    "VERSION": "1.0.0",
    "DISABLE_ERRORS_AND_WARNINGS": True,
    "COERCE_DECIMAL_TO_STRING": True,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "displayOperationId": False,
        "defaultModelExpandDepth": -1,
        "persistAuthorization": True,
        "displayRequestDuration": True,
    },
}
