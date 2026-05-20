from rest_framework import serializers

from .models import Notification


class NotificationSummarySerializer(serializers.ModelSerializer):
    """
    Projection allégée utilisée pour GET /api/v1/notifications/.
    Champs : id, recipientEmail, type, channel, status, createdAt
    """
    recipientEmail = serializers.CharField(source='recipient_email', read_only=True)
    createdAt      = serializers.DateTimeField(source='created_at',  read_only=True)

    class Meta:
        model  = Notification
        fields = ['id', 'recipientEmail', 'type', 'channel', 'status', 'createdAt']

class NotificationDetailSerializer(serializers.ModelSerializer):
    """
    Projection complète utilisée pour GET /api/v1/notifications/{id}/
    et pour les réponses de /send, /read, /retry.
    Tous les champs sont en lecture seule.
    """
    recipientId    = serializers.CharField(source='recipient_id',   read_only=True)
    recipientType  = serializers.CharField(source='recipient_type', read_only=True)
    recipientEmail = serializers.CharField(source='recipient_email', read_only=True)
    ticketId       = serializers.UUIDField(source='ticket_id',  read_only=True, allow_null=True)
    createdAt      = serializers.DateTimeField(source='created_at', read_only=True)
    sentAt         = serializers.DateTimeField(source='sent_at',    read_only=True, allow_null=True)
    readAt         = serializers.DateTimeField(source='read_at',    read_only=True, allow_null=True)
    retryCount     = serializers.IntegerField(source='retry_count', read_only=True)
    errorMessage   = serializers.CharField(
        source='error_message', read_only=True, allow_null=True
    )

    class Meta:
        model  = Notification
        fields = [
            'id', 'recipientId', 'recipientType', 'recipientEmail',
            'type', 'channel', 'subject', 'content', 'status',
            'ticketId', 'createdAt', 'sentAt', 'readAt',
            'retryCount', 'errorMessage',
        ]


# ---------------------------------------------------------------------------
# Notification — Écriture (création)
# ---------------------------------------------------------------------------

class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur d'entrée pour POST /api/v1/notifications/send/.

    Champs attendus (camelCase) :
        recipientId, recipientType, recipientEmail,
        type, channel, ticketId (optionnel), recipientName (optionnel)

    subject et content sont générés automatiquement depuis les
    templates hardcodés (notifications/templates.py) selon (type, channel).
    recipientName est utilisé pour la substitution dans le template
    (si absent, l'email du destinataire est utilisé à la place).
    """
    recipientId    = serializers.CharField(source='recipient_id')
    recipientType  = serializers.ChoiceField(
        choices=['CLIENT', 'AGENT', 'ADMIN'],
        source='recipient_type',
    )
    recipientEmail = serializers.CharField(
        source='recipient_email',
        required=False,
        allow_blank=True,
        default='',
    )
    ticketId       = serializers.UUIDField(
        source='ticket_id',
        required=False,
        allow_null=True,
        default=None,
    )
    # Champ non persisté — uniquement pour la substitution dans le template
    recipientName  = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        write_only=True,
    )

    class Meta:
        model  = Notification
        fields = [
            'recipientId', 'recipientType', 'recipientEmail',
            'type', 'channel', 'ticketId', 'recipientName',
        ]

    def create(self, validated_data):
        # recipientName est write_only et n'existe pas sur le modèle
        validated_data.pop('recipientName', None)
        return super().create(validated_data)


# ---------------------------------------------------------------------------
# NotificationTemplateReadSerializer — lecture seule des templates hardcodés
# ---------------------------------------------------------------------------

class NotificationTemplateReadSerializer(serializers.Serializer):
    """
    Sérialiseur en lecture seule pour exposer les templates hardcodés
    via GET /api/v1/templates/ et GET /api/v1/templates/{type}/{channel}/.
    Aucune persistance en base — les données viennent de templates.py.
    """
    type    = serializers.CharField()
    channel = serializers.CharField()
    subject = serializers.CharField()
    content = serializers.CharField()
