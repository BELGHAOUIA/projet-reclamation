from django.apps import AppConfig
from django.conf import settings
import py_eureka_client.eureka_client as eureka_client
import logging

logger = logging.getLogger(__name__)

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        # On évite d'exécuter l'initialisation Eureka lors des commandes de gestion (migrate, collectstatic, etc.)
        # ou si on est dans le processus de rechargement automatique de Django (runserver)
        import sys
        if 'runserver' in sys.argv:
            try:
                eureka_client.init(
                    eureka_server=settings.EUREKA_SERVER,
                    app_name=settings.APP_NAME,
                    instance_port=settings.EUREKA_INSTANCE_PORT,
                    instance_host=settings.EUREKA_INSTANCE_HOST
                )
                logger.info(f"[{settings.APP_NAME}] Enregistré avec succès sur Eureka à {settings.EUREKA_SERVER}")
            except Exception as e:
                logger.error(f"[{settings.APP_NAME}] Échec de l'enregistrement Eureka : {e}")
