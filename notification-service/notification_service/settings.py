import os
import json
import logging
import urllib.request
from pathlib import Path

# 1. Configuration de base
BASE_DIR = Path(__file__).resolve().parent.parent
APP_NAME = "notification-service"
CONFIG_SERVER_URL = f"http://localhost:9999/{APP_NAME}/default"

_remote_config = {}

# 2. Récupération de la configuration depuis Spring Cloud Config
try:
    with urllib.request.urlopen(CONFIG_SERVER_URL, timeout=5) as resp:
        payload = json.loads(resp.read())
        # On parcourt les sources de propriétés (la première est la plus prioritaire)
        for source in reversed(payload.get("propertySources", [])):
            _remote_config.update(source.get("source", {}))
    logging.info(f"[{APP_NAME}] Configuration chargée depuis le serveur.")
except Exception as e:
    logging.warning(f"[{APP_NAME}] Config Server injoignable : {e}. Utilisation des valeurs par défaut.")

def _cfg(key, default=None):
    return _remote_config.get(key, default)

# 3. Paramètres extraits
SECRET_KEY = _cfg("django.secret_key", 'django-insecure-local-fallback')
DEBUG = True
ALLOWED_HOSTS = ['*']

# Paramètres extraits de la config distante
NOTIFICATION_PORT = int(_cfg("notification-service.port", 8000))
NOTIFICATION_BASE_URL = _cfg("notification-service.base-url", f"http://localhost:{NOTIFICATION_PORT}")
DB_PASSWORD = _cfg("db.password", "")

# 4. Enregistrement sur Eureka
EUREKA_SERVER = _cfg("eureka.client.serviceUrl.defaultZone", "http://localhost:8761/eureka/")
EUREKA_INSTANCE_HOST = _cfg("eureka.instance.hostname", "localhost")
# Note: eureka.instance.port dans le fichier de config semble être 8761 (port du serveur), 
# mais pour l'instance on utilise NOTIFICATION_PORT.


# 5. Reste de la configuration Django (inchangé)
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
        'NAME': BASE_DIR / 'notification_db.sqlite3',
    }
}

# Vos paramètres Email (peuvent aussi être déplacés dans .properties)
EMAIL_HOST_USER = 'boutheinabelg1@gmail.com'
EMAIL_HOST_PASSWORD = 'cfnf myax xiub iykm'