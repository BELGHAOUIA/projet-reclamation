import logging
from uuid import UUID

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import Notification, NotificationStatus
from .serializers import (
    NotificationCreateSerializer,
    NotificationDetailSerializer,
    NotificationSummarySerializer,
    NotificationTemplateReadSerializer,
)
from .templates import NOTIFICATION_TEMPLATES, render_template

logger = logging.getLogger(__name__)


from django.http import JsonResponse
from django.conf import settings

def config_check(request):
    """
    Vue de diagnostic pour vérifier l'origine des configurations.
    Affiche les paramètres non sensibles.
    """
    config_data = {
        "app_name": settings.APP_NAME,
        "config_source": getattr(settings, "_config_source", "UNKNOWN"),
        "config_server_url": settings.CONFIG_SERVER_URL,
        "eureka": {
            "server": settings.EUREKA_SERVER,
            "instance_host": settings.EUREKA_INSTANCE_HOST,
            "instance_port": settings.EUREKA_INSTANCE_PORT,
        },
        "notification_service": {
            "port": settings.NOTIFICATION_PORT,
            "base_url": settings.NOTIFICATION_BASE_URL,
        },
        "database_file": str(settings.DATABASES['default']['NAME']),
        "email_user": settings.EMAIL_HOST_USER, # Visible pour debug, pas le mot de passe
    }
    return JsonResponse(config_data)

def do_send(notification: Notification):
    """
    Envoie la notification selon son canal :
      - EMAIL  → vrai envoi SMTP via django.core.mail
      - SMS    → simulation console (log)
      - IN_APP → simulation console (log)

    Retourne :
        (True,  None)      → succès
        (False, str_error) → échec
    """
    channel = notification.channel

    # ── EMAIL ───────────────────────────────────────────────────────────
    if channel == 'EMAIL':
        try:
            send_mail(
                subject=notification.subject,
                message=notification.content,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient_email],
                fail_silently=False,
            )
            logger.info(
                "Email envoyé — id=%s  destinataire=%s",
                notification.id,
                notification.recipient_email,
            )
            return True, None
        except Exception as exc:
            logger.error("Erreur envoi email — id=%s : %s", notification.id, exc)
            return False, str(exc)

    # ── SMS / IN_APP : simulation console ───────────────────────────────
    try:
        separator = "=" * 62
        log_block = (
            f"\n{separator}\n"
            f"  [NOTIFICATION SERVICE] ENVOI SIMULÉ ({channel})\n"
            f"  ID          : {notification.id}\n"
            f"  Type        : {notification.type}\n"
            f"  Canal       : {channel}\n"
            f"  Destinataire: {notification.recipient_email} "
            f"({notification.recipient_type})\n"
            f"  Sujet       : {notification.subject}\n"
            f"  Contenu     : {notification.content[:100]}"
            f"{'...' if len(notification.content) > 100 else ''}\n"
            f"{separator}"
        )
        print(log_block)
        logger.info(
            "Notification simulée (%s) — id=%s  email=%s",
            channel,
            notification.id,
            notification.recipient_email,
        )
        return True, None

    except Exception as exc:
        logger.error("Erreur inattendue lors de do_send (%s) : %s", channel, exc)
        return False, str(exc)

class NotificationViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """
    ViewSet principal pour la gestion des Notifications.

    Routes standards (via Router) :
        GET    /api/v1/notifications/        → list
        GET    /api/v1/notifications/{id}/   → retrieve
        DELETE /api/v1/notifications/{id}/   → destroy

    Routes personnalisées :
        POST   /api/v1/notifications/send/                     → send
        PATCH  /api/v1/notifications/{id}/read/                → mark_read
        POST   /api/v1/notifications/{id}/retry/               → retry
        GET    /api/v1/notifications/recipient/{recipientId}/  → by_recipient
    """

    queryset = Notification.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ('list', 'by_recipient'):
            return NotificationSummarySerializer
        if self.action == 'send':
            return NotificationCreateSerializer
        return NotificationDetailSerializer

    def list(self, request, *args, **kwargs):
        """
        Retourne la liste paginée des notifications (10 par page).

        Query params optionnels :
            status      → PENDING | SENT | FAILED | READ
            type        → TICKET_CREATED | TICKET_ASSIGNED | ...
            recipientId → UUID du destinataire
        """
        queryset = Notification.objects.all().order_by('-created_at')

        notif_status = request.query_params.get('status')
        notif_type   = request.query_params.get('type')
        recipient_id = request.query_params.get('recipientId')

        if notif_status:
            queryset = queryset.filter(status=notif_status)
        if notif_type:
            queryset = queryset.filter(type=notif_type)
        if recipient_id:
            queryset = queryset.filter(recipient_id=recipient_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = NotificationSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = NotificationSummarySerializer(queryset, many=True)
        return Response(serializer.data)

    # ------------------------------------------------------------------
    # POST /api/v1/notifications/send/
    # ------------------------------------------------------------------

    @action(detail=False, methods=['post'], url_path='send')
    def send(self, request):
        """
        Envoie une notification en utilisant le template hardcodé (type × canal).

        Body attendu :
            recipientId    : UUID
            recipientType  : CLIENT | AGENT
            recipientEmail : email valide
            type           : TICKET_CREATED | TICKET_ASSIGNED | TICKET_RESOLVED
                             | TICKET_ESCALATED | TICKET_UPDATED
            channel        : EMAIL | SMS | IN_APP
            ticketId       : UUID (optionnel)
            recipientName  : str  (optionnel — utilisé dans le message)

        Flux :
          1. Valider les champs d'entrée
          2. Récupérer le template (type, channel) → subject + content auto-générés
          3. Créer la notification (status=PENDING)
          4. Simuler l'envoi → SENT ou FAILED
        """
        serializer = NotificationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated  = serializer.validated_data
        notif_type = validated['type']
        channel    = validated['channel']

        # recipientName est write_only : on l'extrait avant save()
        recipient_name = validated.pop('recipientName', '') or ''

        ticket_id_val = validated.get('ticket_id')
        context = {
            'ticket_id':       str(ticket_id_val) if ticket_id_val else 'N/A',
            'recipient_name':  recipient_name or validated.get('recipient_email', ''),
            'recipient_email': validated.get('recipient_email', ''),
        }

        # Récupérer + remplir le template
        try:
            rendered = render_template(notif_type, channel, context)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Créer la notification en base (status=PENDING)
        notification = serializer.save(
            status=NotificationStatus.PENDING,
            subject=rendered['subject'],
            content=rendered['content'],
        )
        logger.info("Notification créée (PENDING) — id=%s", notification.id)

        # Envoyer la notification
        success, error_msg = do_send(notification)

        if success:
            notification.status  = NotificationStatus.SENT
            notification.sent_at = timezone.now()
            notification.save(update_fields=['status', 'sent_at'])
            logger.info("Notification %s → SENT", notification.id)
        else:
            notification.status        = NotificationStatus.FAILED
            notification.error_message = error_msg
            notification.save(update_fields=['status', 'error_message'])
            logger.warning("Notification %s → FAILED : %s", notification.id, error_msg)

        return Response(
            NotificationDetailSerializer(notification).data,
            status=status.HTTP_201_CREATED,
        )

    # ------------------------------------------------------------------
    # PATCH /api/v1/notifications/{id}/read/
    # ------------------------------------------------------------------

    @action(detail=True, methods=['patch'], url_path='read')
    def mark_read(self, request, pk=None):
        """
        Marque la notification comme lue.
        Passe le status à READ et renseigne readAt.
        Idempotent : retourne 200 si déjà lue.
        """
        notification = self.get_object()

        if notification.status == NotificationStatus.READ:
            return Response(
                {'detail': 'La notification est déjà marquée comme lue.'},
                status=status.HTTP_200_OK,
            )

        notification.status  = NotificationStatus.READ
        notification.read_at = timezone.now()
        notification.save(update_fields=['status', 'read_at'])

        return Response(NotificationDetailSerializer(notification).data)

    # ------------------------------------------------------------------
    # POST /api/v1/notifications/{id}/retry/
    # ------------------------------------------------------------------

    @action(detail=True, methods=['post'], url_path='retry')
    def retry(self, request, pk=None):
        """
        Réessaie l'envoi d'une notification en statut FAILED.

        Flux :
          1. Vérifier que status == FAILED (400 sinon)
          2. Incrémenter retryCount
          3. Simuler le renvoi
          4. Mettre à jour le status → SENT ou FAILED
        """
        notification = self.get_object()

        if notification.status != NotificationStatus.FAILED:
            return Response(
                {
                    'error': (
                        f"Seules les notifications avec status=FAILED peuvent être "
                        f"réessayées. Status actuel : {notification.status}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Incrémenter le compteur avant la tentative
        notification.retry_count += 1
        logger.info(
            "Retry #%d pour la notification %s",
            notification.retry_count,
            notification.id,
        )

        success, error_msg = do_send(notification)

        if success:
            notification.status        = NotificationStatus.SENT
            notification.sent_at       = timezone.now()
            notification.error_message = None
            notification.save(
                update_fields=['status', 'sent_at', 'error_message', 'retry_count']
            )
            logger.info(
                "Notification %s → SENT (retry #%d)",
                notification.id,
                notification.retry_count,
            )
        else:
            notification.status        = NotificationStatus.FAILED
            notification.error_message = error_msg
            notification.save(
                update_fields=['status', 'error_message', 'retry_count']
            )
            logger.warning(
                "Notification %s → FAILED encore (retry #%d) : %s",
                notification.id,
                notification.retry_count,
                error_msg,
            )

        return Response(NotificationDetailSerializer(notification).data)

    # ------------------------------------------------------------------
    # GET /api/v1/notifications/recipient/{recipientId}/
    # ------------------------------------------------------------------

    @action(
        detail=False,
        methods=['get'],
        url_path=r'recipient/(?P<recipient_id>[^/.]+)',
    )
    def by_recipient(self, request, recipient_id=None):
        """
        Retourne les notifications d'un destinataire précis,
        triées par createdAt DESC, avec pagination.
        """
        # Validation du format UUID
        try:
            UUID(str(recipient_id))
        except (ValueError, AttributeError):
            return Response(
                {'error': 'recipientId invalide : format UUID attendu.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = Notification.objects.filter(
            recipient_id=recipient_id
        ).order_by('-created_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = NotificationSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = NotificationSummarySerializer(queryset, many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Templates — lecture seule (hardcodés dans templates.py, pas en base)
# ---------------------------------------------------------------------------

class TemplatesReadView(APIView):
    """
    Expose les templates hardcodés en lecture seule.

    GET /api/v1/templates/
        → liste les 15 combinaisons (type × canal)

    GET /api/v1/templates/{type}/{channel}/
        → détail d'un template précis
        ex: /api/v1/templates/TICKET_CREATED/EMAIL/
    """

    def get(self, request, notif_type=None, channel=None):
        if notif_type and channel:
            key = (notif_type.upper(), channel.upper())
            if key not in NOTIFICATION_TEMPLATES:
                return Response(
                    {
                        'error': (
                            f"Aucun template pour type='{notif_type}' "
                            f"et canal='{channel}'."
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            tmpl = NOTIFICATION_TEMPLATES[key]
            data = {
                'type':    key[0],
                'channel': key[1],
                'subject': tmpl['subject'],
                'content': tmpl['content'],
            }
            return Response(NotificationTemplateReadSerializer(data).data)

        # Liste complète des 15 templates
        data = [
            {
                'type':    k[0],
                'channel': k[1],
                'subject': v['subject'],
                'content': v['content'],
            }
            for k, v in NOTIFICATION_TEMPLATES.items()
        ]
        return Response(NotificationTemplateReadSerializer(data, many=True).data)
