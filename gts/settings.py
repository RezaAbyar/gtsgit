import os
from pathlib import Path
# from .logger import *

BASE_DIR = Path(__file__).resolve().parent.parent

CNF_FILE = os.path.join(BASE_DIR, 'my.cnf')

SECRET_KEY = CNF_FILE

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # My App
    'notification.apps.NotificationConfig',
    'base.apps.BaseConfig',
    'cart.apps.CartConfig',
    'rest_framework',
    'accounts.apps.AccountsConfig',
    'jalali_date',
    'pay.apps.PayConfig',
    'api.apps.ApiConfig',
    'msg.apps.MsgConfig',
    'sell.apps.SellConfig',
    'visit.apps.VisitConfig',
    'blog.apps.BlogConfig',
    'lock.apps.LockConfig',
    'automation.apps.AutomationConfig',
    'drf_api_logger',
    'bazrasnegar.apps.BazrasnegarConfig',
    'rest_framework.authtoken',
    'djangoql',
    'background_task',
    'easy_select2',
    'pm.apps.PmConfig',
    'dashboard.apps.DashboardConfig',
    'silk',
]

MIDDLEWARE = [
    'silk.middleware.SilkyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'base.middlwares.UserAccessMidlware',
    'base.middlwares.UserVisitMidlware',
    'base.middlwares.RequestMiddleware',
    # 'base.middlwares.IsSecureMidlware',
    'drf_api_logger.middleware.api_logger_middleware.APILoggerMiddleware',
    'accounts.middleware.UserDataMiddleware',
]

ROOT_URLCONF = 'gts.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'autoescape': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'customFilter': 'cart.templatetags.customFilter',
                'basefiltertag': 'base.templatetags.basefiltertag',
            }
        },
    },
]

WSGI_APPLICATION = 'gts.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': CNF_FILE,
        }
    },

    'logdb': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': CNF_FILE,
        },
        'TEST': {
            'MIRROR': 'default',
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [

]

LANGUAGE_CODE = 'fa-ir'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = False
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = 'd:/media'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_METADATA_CLASS': 'permission.CustomMetadata'
}


SESSION_COOKIE_AGE = 30 * 60  # 30 دقیقه
SESSION_SAVE_EVERY_REQUEST = True  # کاهش بار CPU
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # عملکرد بهتر
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

DRF_API_LOGGER_DATABASE = True
DRF_LOGGER_INTERVAL = 60
DRF_LOGGER_QUEUE_MAX_SIZE = 100
DRF_API_LOGGER_TIMEDELTA = 210
DRF_API_LOGGER_STATUS_CODES = [402, 400, 405, 404, 500]

PAYROLL_ADD_SABEGHE_IN_YEAR_7GROUP = 685050
MAX_BLACKLIST_COUNT_ALERT = 6800000
MIN_BLACKLIST_COUNT_ALERT = 4000000

TIME_CARD_IN_GS = 10
TIME_CARD_IN_AREA = 90
ALLOWED_CARDS_IN_DAHE = True
MAGFA_USERNAME = CNF_FILE
MAGFA_PASSWORD = CNF_FILE
OTP_MAX_AGE = 2
IS_ARBAIN = False
ID_ENCRYPTION_KEY = b'hfQ5dLoay0DczccR8ZdgCjsugL-b9BQFSHbAbRcs4Sc='
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASS = ''
REDIS_DB = 1
MEDIAURL = 'd:/media'
SEND_MARSOLE_STATUS = 2

WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "BAXF-7oj9p-zx_UBeNNxy2482jRY478wwL6AvAFYp8MQlWcxJRAUObejt3s9uv80IGnyHjTEcXNX1D25QJJ2XFg",
    "VAPID_PRIVATE_KEY": "SU5VhmmRTEVE86jGWvFBylRyvk581FXbDJHYPQWtZDY",
    "VAPID_ADMIN_EMAIL": "rezaabyar@gmail.com"  # ایمیل شما
}

PWA_APP_NAME = 'GTS'
PWA_APP_DESCRIPTION = "سامانه مدیریت و پایش جایگاه"
PWA_APP_THEME_COLOR = '#000000'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'portrait-primary'
PWA_APP_START_URL = '/'
PWA_APP_ICONS = [
    {
        'src': '/static/icons/icon-192x192.png',
        'sizes': '192x192'
    },
    {
        'src': '/static/icons/icon-512x512.png',
        'sizes': '512x512'
    }
]

# SILKY_PYTHON_PROFILER = True
# SILKY_PYTHON_PROFILER_BINARY = True
# SILKY_PYTHON_PROFILER_RESULT_PATH = '/profiles/'
SILKY_META = True
SILKY_AUTHENTICATION = True
SILKY_AUTHORISATION = True
SILKY_MAX_RECORDED_REQUESTS = 10**4
SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10

# تنظیمات Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tehran'