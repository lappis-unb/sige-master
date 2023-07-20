"""
Django settings for sige_master project.
Generated by 'django-admin startproject' using Django 4.2.1.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
LOG_PATH = BASE_DIR / "logs"
ENVFILE_PATH = BASE_DIR / "dev-env"

env = environ.Env(DEBUG=(bool, False))
env.read_env(ENVFILE_PATH)

SECRET_KEY = env("MASTER_SECRET_KEY")
DEBUG = env("ENVIRONMENT") != "production"
ALLOWED_HOSTS = ["*"] if DEBUG else [env("ALLOWED_HOSTS")]


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
    "rest_framework",
    "rest_framework.authtoken",
    "django_rest_passwordreset",
    "corsheaders",
    "drf_spectacular",
    "django_extensions",
    "django_filters",
    "debug_toolbar",
]

LOCAL_APPS = [
    "users",
    "campi",
    "slaves",
    "measurements",
    "transductors",
    "events",
    "groups",
    "unifilar_diagram",
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS


# MIDDLEWARE
# ------------------------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]


# TEMPLATES
# ------------------------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# DATABASES
# ------------------------------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    }
}

# PASSWORDS
# ------------------------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation." "UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation." "MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation." "CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation." "NumericPasswordValidator"},
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

AUTH_USER_MODEL = "users.CustomUser"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # Version 4.2 PKs will be big integers by default
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = ["content-disposition", "accept-encoding", "content-type", "accept", "origin", "authorization"]

APPEND_SLASH = True
LOGIN_REDIRECT_URL = "/"

STATIC_URL = "/static/"

DATE_LOG_FORMAT = "%d/%m/%Y-%H:%M:%S"
DATETIME_ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# DJANGO REST FRAMEWORK
# ------------------------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.TokenAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticatedOrReadOnly",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}


# EMAIL SETTINGS
# ------------------------------------------------------------------------------------------------
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
FRONT_URL = env("FRONT_URL")


# SPECTACULAR SETTINGS
# ---------------------------------------------------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "SIGE - Energy Management System",
    "DESCRIPTION": " Master server - Manage all slaves server and transductors",
    "VERSION": "1.0.0",
    "DISABLE_ERRORS_AND_WARNINGS": True,
}


# LOGGING
# ------------------------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(message)s"},
        "middle": {"format": "%(asctime)s - %(levelname)-6s: %(message)s", "datefmt": DATE_LOG_FORMAT},
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
            "datefmt": DATE_LOG_FORMAT,
        },
    },
    "handlers": {
        "rich": {
            "class": "rich.logging.RichHandler",
            "formatter": "simple",
            "rich_tracebacks": True,
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_PATH / "debug.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB rotative
            "formatter": "middle",
        },
        "tasks-file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_PATH / "tasks" / "tasks.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB rotative
            "backupCount": 5,  # 5 files de backup de 10 MB cada
            "formatter": "middle",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "tasks": {
            "handlers": ["tasks-file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


# DEBUG TOOLBAR
# ------------------------------------------------------------------------------------------------
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    "INTERCEPT_REDIRECTS": False,
    "ALLOWED_HOSTS": ["localhost", "0.0.0.1"],
}
