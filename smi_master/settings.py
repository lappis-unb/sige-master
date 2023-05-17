from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
LOG_PATH = BASE_DIR.joinpath("logs")
ENVFILE_PATH = BASE_DIR.joinpath("dev-env")
LOCALE_PATHS = (BASE_DIR.joinpath("locale"),)

env = environ.Env()
env.read_env(str(ENVFILE_PATH))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("MASTER_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
if env("ENVIRONMENT") == "production":
    DEBUG = False
else:
    DEBUG = True

ALLOWED_HOSTS = ["*"] if DEBUG else [env("ALLOWED_HOSTS")]

# INSTALLED_APPS = [
#     "material.admin.default",
#     "django_cron",
# ]

# APPS
# ------------------------------------------------------------------------------------------------------------------------------------------
DJANGO_APPS = [
    "material.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django.utils.translation",
    "django.contrib.admin",
]

EXTERNAL_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "polymorphic",
    "django_rest_passwordreset",
    "fcm_django",
    "corsheaders",
]

LOCAL_APPS = [
    "campi",
    "slaves",
    "measurements",
    "transductors",
    "users",
    "events",
    "groups",
    "unifilar_diagram",
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS


# MIDDLEWARE
# ------------------------------------------------------------------------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# TEMPLATES
# ------------------------------------------------------------------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR.joinpath("templates")],
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
# ------------------------------------------------------------------------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
        # "TEST": {"NAME": "test_smi-master-dev"},
    }
}

# PASSWORDS
# ------------------------------------------------------------------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation." "UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation." "MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation." "CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation." "NumericPasswordValidator"},
]


# URLS
# ------------------------------------------------------------------------------------------------------------------------------------------
ROOT_URLCONF = "smi_master.urls"
WSGI_APPLICATION = "smi_master.wsgi.application"


# GENERAL
# ------------------------------------------------------------------------------------------------------------------------------------------
LOCALE_NAME = "pt_br"
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_L10N = True
USE_TZ = False
LANGUAGES = (
    ("en", "English"),
    ("pt-br", "Português"),
)

AUTH_USER_MODEL = "users.CustomUser"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # Version 4.2 PKs will be big integers by default

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = ["content-disposition", "accept-encoding", "content-type", "accept", "origin", "authorization"]

CRON_CLASSES = ["slaves.cronjob.CheckTransductorBrokenCronjob", "slaves.cronjob.GetAllMeasurementsCronjob"]

APPEND_SLASH = False
LOGIN_REDIRECT_URL = "/"

# STATIC FILES AND MEDIA
# ------------------------------------------------------------------------------------------------------------------------------------------
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(BASE_DIR / "static")]
MEDIA_ROOT = str(BASE_DIR / "media")
MEDIA_URL = "/media/"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


# LOGGING
# ------------------------------------------------------------------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {"level": "DEBUG", "class": "logging.FileHandler", "filename": BASE_DIR.joinpath("debug.log")},
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}


# MATERIAL ADMIN
# ------------------------------------------------------------------------------------------------------------------------------------------
MATERIAL_ADMIN_SITE = {
    "HEADER": "Your site header",  # Admin site header
    "TITLE": "Your site title",  # Admin site title
    # # Admin site favicon (path to static should be specified)
    # 'FAVICON': 'path/to/favicon',
    # 'MAIN_BG_COLOR': '#FFFFFF',  # Admin site main color, css color should be specified
    # # Admin site main hover color, css color should be specified
    # 'MAIN_HOVER_COLOR': '#FFFFFF',
    # # Admin site profile picture (path to static should be specified)
    "PROFILE_PICTURE": "/img/proj_trans_l.png",
    # # Admin site profile background (path to static should be specified)
    # 'PROFILE_BG': 'path/to/image',
    # # Admin site logo on login page (path to static should be specified)
    # 'LOGIN_LOGO': 'path/to/image',
    # # Admin site background on login/logout pages (path to static should be specified)
    # 'LOGOUT_BG': 'path/to/image',
    "SHOW_THEMES": True,  # Show default admin themes button
    "TRAY_REVERSE": True,  # Hide object-tools and additional-submit-line by default
    "NAVBAR_REVERSE": True,  # Hide side navbar by default
    # 'SHOW_COUNTS': True,  # Show instances counts for each model
    # 'APP_ICONS': {  # Set icons for applications(lowercase), including 3rd party apps, {'application_name': 'material_icon_name', ...}
    #     'sites': 'send',
    # },
    # 'MODEL_ICONS': {  # Set icons for models(lowercase), including 3rd party models, {'model_name': 'material_icon_name', ...}
    #     'site': 'contact_mail',
    # }
}

# FCM SETTINGS
# ------------------------------------------------------------------------------------------------------------------------------------------
FCM_DJANGO_SETTINGS = {
    "APP_VERBOSE_NAME": "[string for AppConfig's verbose_name]",
    # default: 'FCM Django')
    "FCM_SERVER_KEY": env("API_KEY"),
    # true if you want to have only one active device per registered user at a time
    # default: False
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": True,
}

# EMAIL SETTINGS
# ------------------------------------------------------------------------------------------------------------------------------------------
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True

FRONT_URL = env("FRONT_URL")


# django-rest-framework
# ------------------------------------------------------------------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.TokenAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticatedOrReadOnly",),
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}
