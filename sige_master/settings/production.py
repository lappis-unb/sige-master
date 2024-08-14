# flake8: noqa
# pylint: skip-file

from datetime import time, timedelta

import environ

from sige_master.settings.common import *

env = environ.Env()
env.read_env(BASE_DIR / "./.envs/.env.prod")


SITE_NAME = "MEPA - Monitoramento de Energia em Plataforma Aberta"
ADMIN_URL = env("DJANGO_ADMIN_URL", default="management/")
DOMAIN = env("DOMAIN_NAME")

DEBUG = env.bool("DJANGO_DEBUG", False)
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS")


# TARIFF ENERGY SETTINGS (Taxa de energia em R$/kWh)
# ------------------------------------------------------------------------------------------------

TARIFF_PEAK = env.float("TARIFF_PEAK", default=1.20)
TARIFF_OFF_PEAK = env.float("TARIFF_PEAK", default=0.70)

LIMIT_FILTER = env.int("LIMIT_FILTER", default=500)


# DATABASES
# ------------------------------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
    }
}

DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=100)


# SIMPLE JWT SETTINGS
# ---------------------------------------------------------------------------------------------------------------------

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "SIGNING_KEY": env("SIGNING_KEY"),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
}


# EMAIL SETTINGS
# -----------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env("EMAIL_PORT")
ACCOUNT_EMAIL_VERIFICATION = "none"
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL")
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)


# STATICFILES whitenoise (Unless CDN or Nginx)
# -----------------------------------------------------------------------------

# STORAGES = {
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }

