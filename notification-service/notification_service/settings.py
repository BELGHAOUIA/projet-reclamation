from pathlib import Path
import urllib.request
import json
import logging

CONFIG_SERVER_URL = "http://localhost:9999/services/default"
_remote_config = {}

try:
    with urllib.request.urlopen(CONFIG_SERVER_URL, timeout=3) as _resp:
        _payload = json.loads(_resp.read())
        for _source in reversed(_payload.get("propertySources", [])):
            _remote_config.update(_source.get("source", {}))
except Exception as _e:
    logging.warning(
        f"[config-client] Config Server indisponible ({CONFIG_SERVER_URL}) : {_e}. "
        "Les valeurs locales seront utilisées."
    )

def _cfg(key, default=None):
    """Lecture d'une clé depuis la config centralisée."""
    return _remote_config.get(key, default)

GLOBAL_PARAM_P1 = int(_cfg("global.params.p1", 555))
GLOBAL_PARAM_P2 = int(_cfg("global.params.p2", 777))

NOTIFICATION_PORT     = int(_cfg("notification-service.port", 8000))
NOTIFICATION_BASE_URL = _cfg("notification-service.base-url", f"http://localhost:{NOTIFICATION_PORT}")


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-notification-svc-change-me-in-production-!!!'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'notification_service.urls'

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

WSGI_APPLICATION = 'notification_service.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   BASE_DIR / 'notification_db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True


STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------------------------------------------------
# Django REST Framework
# -----------------------------------------------------------------------
REST_FRAMEWORK = {
    # Pagination : 10 éléments par page, navigation via ?page=N
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    # Renderers : JSON + API navigable (utile pendant le développement)
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],

    # Parsers
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}


EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'boutheinabelg1@gmail.com' 
EMAIL_HOST_PASSWORD = 'cfnf myax xiub iykm'       
DEFAULT_FROM_EMAIL  = f'Notification Service <{EMAIL_HOST_USER}>'


LOGGING = {
    'version':                  1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} — {message}',
            'style':  '{',
        },
    },
    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level':    'INFO',
    },
    'loggers': {
        'notifications': {
            'handlers':  ['console'],
            'level':     'DEBUG',
            'propagate': False,
        },
    },
}
