# flake8: noqa
# pylint: skip-file

from datetime import timedelta

import environ

from sige_master.settings.common import *

env = environ.Env()
env.read_env(BASE_DIR / "./.envs/.env.dev")

SITE_NAME = "MEPA - Monitoramento de Energia em Plataforma Aberta"
ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")
DOMAIN = env("DOMAIN_NAME")


DEBUG = env.bool("DJANGO_DEBUG", True)
SECRET_KEY = env("DJANGO_SECRET", default="django-insecure-#123!@#$%^&*()_+")
CSRF_TRUSTED_ORIGINS = ["http://localhost:8001"]
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]


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

# SIMPLE JWT SETTINGS
# ---------------------------------------------------------------------------------------------------------------------

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=10),
    "SIGNING_KEY": env("SIGNING_KEY", default="SECRET"),
    "ROTATE_REFRESH_TOKENS": True,
}


# EMAIL SETTINGS
# -----------------------------------------------------------------------------
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env("EMAIL_PORT", default=1025)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ACCOUNT_EMAIL_VERIFICATION = "none"
DEFAULT_FROM_EMAIL = ""


# DEBUG TOOLBAR
# -----------------------------------------------------------------------------
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
INSTALLED_APPS += ["debug_toolbar"]
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    "INTERCEPT_REDIRECTS": False,
    "ALLOWED_HOSTS": ["*"],
}


# DJANGO EXTENSIONS
# -----------------------------------------------------------------------------
INSTALLED_APPS += ["django_extensions"]


# DJANGO PDB
# -----------------------------------------------------------------------------
# MIDDLEWARE += ["django_pdb.middleware.PdbMiddleware"]
# INSTALLED_APPS += ["django_pdb"]
# MIDDLEWARE += ["django_pdb.middleware.PdbMiddleware"]
# INSTALLED_APPS += ["django_pdb"]
