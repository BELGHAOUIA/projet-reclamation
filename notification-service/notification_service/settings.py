import os
import json
import urllib.request
from pathlib import Path

# =========================================================
# BASE CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

APP_NAME = "notification-service"

CONFIG_SERVER_URL = os.getenv(
    "CONFIG_SERVER_URL",
    f"http://localhost:9999/{APP_NAME}/default"
)

_remote_config = {}

# =========================================================
# LOAD CONFIGURATION FROM SPRING CLOUD CONFIG SERVER
# =========================================================

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
    print(f"❌ Config Server error: {e}")
    print("⚠️ Using local fallback configuration")

# =========================================================
# HELPER
# =========================================================

def _cfg(key, default=None):
    return _remote_config.get(key, default)

# =========================================================
# DJANGO SETTINGS
# =========================================================

SECRET_KEY = _cfg(
    "django.secret_key",
    "django-insecure-local-fallback"
)

DEBUG = True

ALLOWED_HOSTS = ["*"]

# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

APPLICATION_NAME = _cfg(
    "spring.application.name",
    "notification-service"
)

NOTIFICATION_PORT = int(
    _cfg("notification-service.port", 8003)
)

NOTIFICATION_BASE_URL = _cfg(
    "notification-service.base-url",
    f"http://localhost:{NOTIFICATION_PORT}"
)

# =========================================================
# EUREKA CONFIGURATION
# =========================================================

EUREKA_SERVER = _cfg(
    "eureka.client.serviceUrl.defaultZone",
    "http://localhost:8761/eureka/"
)

DISCOVERY_ENABLED = str(
    _cfg("spring.cloud.discovery.enabled", "true")
).lower() == "true"

# =========================================================
# DATABASE
# =========================================================

DB_PASSWORD = _cfg(
    "db.password",
    ""
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'notification_db.sqlite3',
    }
}

# =========================================================
# EMAIL CONFIGURATION
# =========================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = _cfg(
    "spring.mail.host",
    "smtp.gmail.com"
)

EMAIL_PORT = int(
    _cfg("spring.mail.port", 587)
)

EMAIL_HOST_USER = _cfg(
    "spring.mail.username",
    ""
)

EMAIL_HOST_PASSWORD = _cfg(
    "spring.mail.password",
    ""
)

EMAIL_USE_TLS = str(
    _cfg(
        "spring.mail.properties.mail.smtp.starttls.enable",
        "true"
    )
).lower() == "true"

EMAIL_USE_SSL = False

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
# URLS / WSGI
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
# STATIC FILES
# =========================================================

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

# =========================================================
# LOGGING
# =========================================================

print("\n========== CONFIGURATION ==========")
print(f"Application Name : {APPLICATION_NAME}")
print(f"Notification Port: {NOTIFICATION_PORT}")
print(f"Base URL         : {NOTIFICATION_BASE_URL}")
print(f"Eureka Server    : {EUREKA_SERVER}")
print(f"Discovery Enabled: {DISCOVERY_ENABLED}")
print(f"Email User       : {EMAIL_HOST_USER}")
print("===================================\n")