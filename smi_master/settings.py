import os

import environ
from django.utils.translation import gettext_lazy as _
from unipath import Path

env = environ.Env()
env.read_env('dev-env')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('MASTER_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
if env('ENVIRONMENT') is 'production':
    DEBUG = False
else:
    DEBUG = True

PROJECT_DIR = Path(__file__).parent.parent
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': PROJECT_DIR + '/debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

ALLOWED_HOSTS = [env('ALLOWED_HOSTS')]


# Application definition

INSTALLED_APPS = [
    'material.admin',
    'material.admin.default',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django_cron',
    'polymorphic',
    'rest_framework',
    'rest_framework.authtoken',
    'campi',
    'slaves',
    'measurements',
    'transductors',
    # 'users',
    'corsheaders',
    'events',
    'rosetta',
]

CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'smi_master.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CRON_CLASSES = [
    "slaves.cronjob.CheckTransductorBrokenCronjob",
    "slaves.cronjob.GetAllMeasurementsCronjob"
]

WSGI_APPLICATION = 'smi_master.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT')
    }
}

if env('ENVIRONMENT') == 'development':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    )
}

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LOCALE_NAME = 'pt_BR'
LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
LANGUAGES = (
    ('en', u'English'),
    ('pt-br', u'Português'),
)
# LOCALE_PATHS = (
#     os.path.join(os.path.dirname(__file__), "locale"),
# )

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale/'),)


USE_L10N = True

# USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

# AUTH_USER_MODEL = 'users.CustomUser'

LOCALE_PATHS = (PROJECT_DIR + '/locale', )


MATERIAL_ADMIN_SITE = {
    'HEADER': _('Your site header'),  # Admin site header
    'TITLE': _('Your site title'),  # Admin site title
    # # Admin site favicon (path to static should be specified)
    # 'FAVICON': 'path/to/favicon',
    # 'MAIN_BG_COLOR': '#FFFFFF',  # Admin site main color, css color should be specified
    # # Admin site main hover color, css color should be specified
    # 'MAIN_HOVER_COLOR': '#FFFFFF',
    # # Admin site profile picture (path to static should be specified)
    'PROFILE_PICTURE': '/img/proj_trans_l.png',
    # # Admin site profile background (path to static should be specified)
    # 'PROFILE_BG': 'path/to/image',
    # # Admin site logo on login page (path to static should be specified)
    # 'LOGIN_LOGO': 'path/to/image',
    # # Admin site background on login/logout pages (path to static should be specified)
    # 'LOGOUT_BG': 'path/to/image',
    'SHOW_THEMES': True,  # Show default admin themes button
    'TRAY_REVERSE': True,  # Hide object-tools and additional-submit-line by default
    'NAVBAR_REVERSE': True,  # Hide side navbar by default
    # 'SHOW_COUNTS': True,  # Show instances counts for each model
    # 'APP_ICONS': {  # Set icons for applications(lowercase), including 3rd party apps, {'application_name': 'material_icon_name', ...}
    #     'sites': 'send',
    # },
    # 'MODEL_ICONS': {  # Set icons for models(lowercase), including 3rd party models, {'model_name': 'material_icon_name', ...}
    #     'site': 'contact_mail',
    # }
}

# Using temp gmail account
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'unb.smi@gmail.com'
EMAIL_HOST_PASSWORD = 'g^C4bN4nTDL}obv+'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
