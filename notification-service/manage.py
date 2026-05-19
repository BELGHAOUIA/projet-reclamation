#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    args = list(sys.argv)

    # When 'runserver' is called without an explicit address:port,
    # automatically use the port defined in NOTIFICATION_PORT (from config server).
    if len(args) >= 2 and args[1] == 'runserver' and len(args) == 2:
        try:
            from django.conf import settings
            port = getattr(settings, 'NOTIFICATION_PORT', 8083)
            args.append(f'0.0.0.0:{port}')
        except Exception:
            args.append('0.0.0.0:8083')  # hard fallback

    execute_from_command_line(args)


if __name__ == '__main__':
    main()
