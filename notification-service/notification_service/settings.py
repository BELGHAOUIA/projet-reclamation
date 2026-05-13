"""
Django Settings - CORRIGÉ pour Spring Cloud Config Server et Eureka
Remplace le settings.py original avec support Eureka correct
"""

import os
import json
import urllib.request
from pathlib import Path

# =========================================================
# BASE CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

APP_NAME = os.getenv("SPRING_APPLICATION_NAME", "notification-service")

# =========================================================
# CONFIG SERVER - Chargement Configuration Centralisée
# =========================================================

CONFIG_SERVER_URL = os.getenv(
    "CONFIG_SERVER_URL",
    "http://localhost:9999/notification-service/default"
)

_remote_config = {}

try:
    print(f"🔄 Loading configuration from: {CONFIG_SERVER_URL}")
    
    with urllib.request.urlopen(CONFIG_SERVER_URL, timeout=10) as response:
        raw_data = response.read().decode("utf-8")
        payload = json.loads(raw_data)
        property_sources = payload.get("propertySources", [])
        
        # Highest priority last
        for source in reversed(property_sources):
            _remote_config.update(source.get("source", {}))
    
    print("✅ Remote configuration loaded successfully")

except Exception as e:
    print(f"⚠️  Config Server error: {e}")
    print("   Using local fallback configuration")

# =========================================================
# HELPER FUNCTION
# =========================================================

def _cfg(key, default=None):
    """Get config value from remote config or default"""
    return _remote_config.get(key, default)

# =========================================================
# DJANGO SECURITY
# =========================================================

SECRET_KEY = _cfg(
    "django.secret_key",
    "django-insecure-local-fallback-change-in-production"
)

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# =========================================================
# APPLICATION INFORMATION
# =========================================================

APPLICATION_NAME = _cfg("spring.application.name", APP_NAME)

# =========================================================
# SERVER CONFIGURATION
# =========================================================

NOTIFICATION_PORT = int(
    os.getenv(
        "NOTIFICATION_PORT",
        _cfg("notification-service.port", 8000)
    )
)

NOTIFICATION_BASE_URL = os.getenv(
    "NOTIFICATION_BASE_URL",
    _cfg("notification-service.base-url", f"http://localhost:{NOTIFICATION_PORT}")
)

# =========================================================
# EUREKA DISCOVERY - ✅ CORRECTED
# =========================================================

# ✅ PROPRIÉTÉS EUREKA - Maintenant correctement définies!
EUREKA_SERVER = os.getenv(
    "EUREKA_CLIENT_SERVICE_URL_DEFAULTZONE",
    _cfg("eureka.client.serviceUrl.defaultZone", "http://localhost:8761/eureka/")
)

EUREKA_HOSTNAME = os.getenv(
    "EUREKA_INSTANCE_HOSTNAME",
    _cfg("eureka.instance.hostname", "localhost")
)

# ✅ LA PROPRIÉTÉ MANQUANTE QUI CAUSAIT L'ERREUR!
EUREKA_INSTANCE_PORT = int(
    os.getenv(
        "EUREKA_INSTANCE_PORT",
        NOTIFICATION_PORT  # ← Utiliser le port du service
    )
)

# ✅ Autres propriétés Eureka
EUREKA_INSTANCE_ID = os.getenv(
    "EUREKA_INSTANCE_ID",
    _cfg("eureka.instance.instance-id", f"{APP_NAME}:instance-{os.getenv('HOSTNAME', 'local')}")
)

EUREKA_STATUS_PAGE_URL = os.getenv(
    "EUREKA_STATUS_PAGE_URL",
    _cfg("eureka.instance.status-page-url-path", f"http://{EUREKA_HOSTNAME}:{EUREKA_INSTANCE_PORT}/")
)

EUREKA_HEALTH_CHECK_URL = os.getenv(
    "EUREKA_HEALTH_CHECK_URL",
    _cfg("eureka.instance.health-check-url-path", f"http://{EUREKA_HOSTNAME}:{EUREKA_INSTANCE_PORT}/health/")
)

EUREKA_LEASE_RENEWAL_INTERVAL = int(
    _cfg("eureka.instance.lease-renewal-interval-in-seconds", 30)
)

EUREKA_LEASE_EXPIRATION_DURATION = int(
    _cfg("eureka.instance.lease-expiration-duration-in-seconds", 90)
)

DISCOVERY_ENABLED = str(
    _cfg("spring.cloud.discovery.enabled", "true")
).lower() == "true"

# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'notification_db.sqlite3',
    }
}

# Optionnel: PostgreSQL
DB_ENGINE = _cfg("spring.datasource.driver-class-name", "sqlite")
if "postgresql" in DB_ENGINE.lower():
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _cfg("spring.datasource.database", "notification_db"),
        'USER': _cfg("spring.datasource.username", "notification_user"),
        'PASSWORD': os.getenv("DB_PASSWORD", _cfg("spring.datasource.password", "")),
        'HOST': _cfg("spring.datasource.host", "localhost"),
        'PORT': _cfg("spring.datasource.port", "5432"),
    }

# =========================================================
# EMAIL CONFIGURATION
# =========================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv(
    "SPRING_MAIL_HOST",
    _cfg("spring.mail.host", "smtp.gmail.com")
)

EMAIL_PORT = int(
    os.getenv(
        "SPRING_MAIL_PORT",
        _cfg("spring.mail.port", 587)
    )
)

EMAIL_HOST_USER = os.getenv(
    "SPRING_MAIL_USERNAME",
    _cfg("spring.mail.username", "")
)

EMAIL_HOST_PASSWORD = os.getenv(
    "SPRING_MAIL_PASSWORD",
    _cfg("spring.mail.password", "")
)

EMAIL_USE_TLS = str(
    os.getenv(
        "SPRING_MAIL_PROPERTIES_MAIL_SMTP_STARTTLS_ENABLE",
        _cfg("spring.mail.properties.mail.smtp.starttls.enable", "true")
    )
).lower() == "true"

EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL = f"Notification Service <{EMAIL_HOST_USER}>"

# =========================================================
# DJANGO APPS
# =========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'notifications.apps.NotificationsConfig',
]

# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =========================================================
# URL & WSGI CONFIGURATION
# =========================================================

ROOT_URLCONF = 'notification_service.urls'
WSGI_APPLICATION = 'notification_service.wsgi.application'

# =========================================================
# TEMPLATES
# =========================================================

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

# =========================================================
# AUTHENTICATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================================================
# REST FRAMEWORK CONFIGURATION
# =========================================================

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(_cfg("app.pagination.default-page-size", 10)),
    
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

# =========================================================
# LOGGING CONFIGURATION
# =========================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} — {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'notifications': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# =========================================================
# CONFIGURATION SUMMARY - Print at Startup
# =========================================================

print("\n" + "="*60)
print("📋 DJANGO CONFIGURATION SUMMARY")
print("="*60)
print(f"Application Name      : {APPLICATION_NAME}")
print(f"Server Port           : {NOTIFICATION_PORT}")
print(f"Base URL              : {NOTIFICATION_BASE_URL}")
print()
print("🎯 EUREKA CONFIGURATION (✅ CORRECTED):")
print(f"  Eureka Server       : {EUREKA_SERVER}")
print(f"  Instance Hostname   : {EUREKA_HOSTNAME}")
print(f"  Instance Port       : {EUREKA_INSTANCE_PORT}  ← ✅ NOW DEFINED!")
print(f"  Instance ID         : {EUREKA_INSTANCE_ID}")
print(f"  Health Check URL    : {EUREKA_HEALTH_CHECK_URL}")
print(f"  Discovery Enabled   : {DISCOVERY_ENABLED}")
print()
print("📧 EMAIL CONFIGURATION:")
print(f"  Host                : {EMAIL_HOST}")
print(f"  Port                : {EMAIL_PORT}")
print(f"  Username            : {EMAIL_HOST_USER}")
print(f"  TLS Enabled         : {EMAIL_USE_TLS}")
print()
print("💾 DATABASE:")
print(f"  Engine              : {DATABASES['default']['ENGINE']}")
print(f"  Name                : {DATABASES['default']['NAME']}")
print()
print("="*60 + "\n")