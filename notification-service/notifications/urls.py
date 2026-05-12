"""
URLs du Notification Service.

Toutes les routes sont montées sous /api/v1/.

Notifications :
    POST   /api/v1/notifications/send/                     → envoyer
    GET    /api/v1/notifications/                          → lister (filtres: status, type, recipientId)
    GET    /api/v1/notifications/{id}/                     → détail
    PATCH  /api/v1/notifications/{id}/read/                → marquer comme lue
    POST   /api/v1/notifications/{id}/retry/               → réessayer si FAILED
    GET    /api/v1/notifications/recipient/{recipientId}/  → notifs d'un destinataire
    DELETE /api/v1/notifications/{id}/                     → supprimer

Templates (lecture seule — hardcodés dans templates.py) :
    GET    /api/v1/templates/                              → lister les 15 templates
    GET    /api/v1/templates/{type}/{channel}/             → un template précis
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet, TemplatesReadView, config_check

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('api/v1/config/', config_check, name='config_check'),
    path('api/v1/', include(router.urls)),
    # Templates en lecture seule
    path('api/v1/templates/', TemplatesReadView.as_view()),
    path('api/v1/templates/<str:notif_type>/<str:channel>/', TemplatesReadView.as_view()),
]
