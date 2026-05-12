from django.contrib import admin

from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display   = [
        'id', 'recipient_email', 'recipient_type',
        'type', 'channel', 'status', 'retry_count', 'created_at',
    ]
    list_filter    = ['status', 'type', 'channel', 'recipient_type']
    search_fields  = ['recipient_email', 'subject', 'id']
    readonly_fields = ['id', 'created_at', 'sent_at', 'read_at']
    ordering       = ['-created_at']
    list_per_page  = 25

    fieldsets = (
        ('Destinataire', {
            'fields': ('recipient_id', 'recipient_type', 'recipient_email'),
        }),
        ('Message', {
            'fields': ('type', 'channel', 'subject', 'content', 'ticket_id'),
        }),
        ('Statut & Suivi', {
            'fields': (
                'status', 'retry_count', 'error_message',
                'created_at', 'sent_at', 'read_at',
            ),
        }),
    )
