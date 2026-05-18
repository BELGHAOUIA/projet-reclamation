import logging
import os
import sys

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        # Skip during management commands (migrate, collectstatic, shell, …)
        # Register only when an actual web server is starting.
        web_commands = {'runserver', 'gunicorn', 'uvicorn', 'daphne'}
        is_web = (
            any(cmd in sys.argv for cmd in web_commands)
            or 'gunicorn' in sys.modules
        )
        if not is_web:
            return

        # Django dev-server autoreloader: the parent watcher process also
        # calls ready(), but RUN_MAIN is only set to 'true' in the child
        # (the real server process). Skip registration in the parent.
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return

        self._register_eureka()

    def _register_eureka(self):
        try:
            import py_eureka_client.eureka_client as eureka_client
        except ImportError:
            logger.warning(
                "[eureka] py_eureka_client n'est pas installé — "
                "enregistrement Eureka ignoré."
            )
            return

        from django.conf import settings as django_settings

        eureka_server   = getattr(django_settings, 'EUREKA_SERVER',        'http://localhost:8761/eureka/')
        # APP_NAME is 'notification-service'; Eureka names are case-insensitive
        # but the gateway expects lb:http://NOTIFICATION-SERVICE (uppercase).
        app_name        = getattr(django_settings, 'APP_NAME',             'notification-service').upper()
        instance_port   = getattr(django_settings, 'EUREKA_INSTANCE_PORT', 8083)
        # EUREKA_HOSTNAME is the correct attribute name defined in settings.py
        instance_host   = getattr(django_settings, 'EUREKA_HOSTNAME',      'localhost')

        try:
            eureka_client.init(
                eureka_server=eureka_server,
                app_name=app_name,
                instance_port=instance_port,
                instance_host=instance_host,
            )
            logger.info(
                "[eureka] '%s' enregistré sur %s (hôte=%s, port=%d)",
                app_name, eureka_server, instance_host, instance_port,
            )
        except Exception as exc:
            logger.error("[eureka] Enregistrement échoué : %s", exc)
