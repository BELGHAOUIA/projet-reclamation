import os
import json
import logging
import urllib.request
from pathlib import Path
import py_eureka_client.eureka_client as eureka

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

# Paramètres Métier
GLOBAL_PARAM_P1 = int(_cfg("global.params.p1", 555))
GLOBAL_PARAM_P2 = int(_cfg("global.params.p2", 777))
NOTIFICATION_PORT = int(_cfg("notification-service.port", 8000))

# 4. Enregistrement sur Eureka
EUREKA_SERVER = _cfg("eureka.client.serviceUrl.defaultZone", "http://localhost:8761/eureka/")

async def init_eureka():
    await eureka.init(
        eureka_server=EUREKA_SERVER,
        app_name=APP_NAME,
        instance_port=NOTIFICATION_PORT,
        instance_host=_cfg("eureka.instance.hostname", "localhost")
    )

# Appel de l'initialisation Eureka (pour Django, cela peut être mis dans apps.py)
# import asyncio
# asyncio.run(init_eureka())

# 5. Reste de la configuration Django (inchangé)
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'notification_db.sqlite3',
    }
}

# Vos paramètres Email (peuvent aussi être déplacés dans .properties)
EMAIL_HOST_USER = 'boutheinabelg1@gmail.com'
EMAIL_HOST_PASSWORD = 'cfnf myax xiub iykm'