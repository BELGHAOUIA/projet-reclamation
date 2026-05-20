import uuid
from django.db import models

class RecipientType(models.TextChoices):
    CLIENT = 'CLIENT', 'Client'
    AGENT  = 'AGENT',  'Agent'
    ADMIN  = 'ADMIN',  'Administrateur'


class NotificationType(models.TextChoices):
    TICKET_CREATED   = 'TICKET_CREATED',   'Ticket créé'
    TICKET_ASSIGNED  = 'TICKET_ASSIGNED',  'Ticket assigné'
    TICKET_RESOLVED  = 'TICKET_RESOLVED',  'Ticket résolu'
    TICKET_ESCALATED = 'TICKET_ESCALATED', 'Ticket escaladé'
    TICKET_UPDATED   = 'TICKET_UPDATED',   'Ticket mis à jour'


class Channel(models.TextChoices):
    EMAIL  = 'EMAIL',  'E-mail'
    SMS    = 'SMS',    'SMS'
    IN_APP = 'IN_APP', 'In-App'


class NotificationStatus(models.TextChoices):
    PENDING = 'PENDING', 'En attente'
    SENT    = 'SENT',    'Envoyée'
    FAILED  = 'FAILED',  'Échouée'
    READ    = 'READ',    'Lue'

class Notification(models.Model):

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_id   = models.TextField(db_index=True)
    recipient_type = models.CharField(max_length=10, choices=RecipientType.choices)
    recipient_email = models.CharField(max_length=255, blank=True, default='')
    type           = models.CharField(max_length=30, choices=NotificationType.choices)
    channel        = models.CharField(max_length=10, choices=Channel.choices)
    subject        = models.CharField(max_length=255)
    content        = models.TextField()
    status         = models.CharField(
        max_length=10,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        db_index=True,
    )
    ticket_id      = models.UUIDField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True, db_index=True)
    sent_at        = models.DateTimeField(null=True, blank=True)
    read_at        = models.DateTimeField(null=True, blank=True)
    retry_count    = models.IntegerField(default=0)
    error_message  = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient_id', '-created_at']),
            models.Index(fields=['status', 'type']),
        ]

    def __str__(self):
        return (
            f"[{self.status}] {self.type} → {self.recipient_email} "
            f"(canal: {self.channel})"
        )


