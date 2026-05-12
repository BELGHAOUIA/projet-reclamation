"""
Templates de notifications hardcodés — organisés par (type, channel).

Clé    : (NotificationType, Channel)
Valeur : dict avec 'subject' et 'content'

Variables disponibles dans les chaînes (substitution via str.format) :
  {ticket_id}       → UUID du ticket (ou "N/A" si absent)
  {recipient_name}  → nom du destinataire (ou son email si non fourni)
  {recipient_email} → email du destinataire

15 combinaisons : 5 types × 3 canaux (EMAIL | SMS | IN_APP)
"""

NOTIFICATION_TEMPLATES = {

    # ---------------------------------------------------------------
    # TICKET_CREATED
    # ---------------------------------------------------------------
    ('TICKET_CREATED', 'EMAIL'): {
        'subject': 'Votre ticket {ticket_id} a été créé',
        'content': (
            "Bonjour {recipient_name},\n\n"
            "Votre ticket de réclamation (réf. {ticket_id}) a bien été enregistré.\n"
            "Notre équipe Support vous contactera dans les 24 heures ouvrées.\n\n"
            "Cordialement,\n"
            "L'équipe Support Client"
        ),
    },
    ('TICKET_CREATED', 'SMS'): {
        'subject': 'Ticket créé',
        'content': (
            "[Support] Ticket {ticket_id} créé. "
            "Notre équipe vous contactera sous 24h. Merci."
        ),
    },
    ('TICKET_CREATED', 'IN_APP'): {
        'subject': 'Nouveau ticket enregistré',
        'content': (
            "Votre ticket {ticket_id} a été enregistré avec succès. "
            "Vous serez notifié à chaque mise à jour."
        ),
    },

    # ---------------------------------------------------------------
    # TICKET_ASSIGNED
    # ---------------------------------------------------------------
    ('TICKET_ASSIGNED', 'EMAIL'): {
        'subject': 'Le ticket {ticket_id} vous a été assigné',
        'content': (
            "Bonjour {recipient_name},\n\n"
            "Le ticket (réf. {ticket_id}) vient d'être assigné à votre file de traitement.\n"
            "Merci de le prendre en charge dès que possible.\n\n"
            "Cordialement,\n"
            "L'équipe Support"
        ),
    },
    ('TICKET_ASSIGNED', 'SMS'): {
        'subject': 'Ticket assigné',
        'content': (
            "[Support] Ticket {ticket_id} assigné à votre file. "
            "Veuillez le traiter dès que possible."
        ),
    },
    ('TICKET_ASSIGNED', 'IN_APP'): {
        'subject': 'Nouveau ticket dans votre file',
        'content': (
            "Le ticket {ticket_id} vient d'être assigné à votre file. "
            "Cliquez pour consulter les détails."
        ),
    },

    # ---------------------------------------------------------------
    # TICKET_RESOLVED
    # ---------------------------------------------------------------
    ('TICKET_RESOLVED', 'EMAIL'): {
        'subject': 'Votre ticket {ticket_id} a été résolu',
        'content': (
            "Bonjour {recipient_name},\n\n"
            "Nous avons le plaisir de vous informer que votre ticket (réf. {ticket_id}) "
            "a été traité et résolu.\n"
            "Si vous avez d'autres questions, n'hésitez pas à nous contacter.\n\n"
            "Cordialement,\n"
            "L'équipe Support Client"
        ),
    },
    ('TICKET_RESOLVED', 'SMS'): {
        'subject': 'Ticket résolu',
        'content': (
            "[Support] Votre ticket {ticket_id} a été résolu. "
            "Contactez-nous si besoin."
        ),
    },
    ('TICKET_RESOLVED', 'IN_APP'): {
        'subject': 'Ticket résolu',
        'content': (
            "Votre ticket {ticket_id} a été résolu. "
            "Consultez votre espace client pour les détails de la solution."
        ),
    },

    # ---------------------------------------------------------------
    # TICKET_ESCALATED
    # ---------------------------------------------------------------
    ('TICKET_ESCALATED', 'EMAIL'): {
        'subject': 'Votre ticket {ticket_id} a été escaladé',
        'content': (
            "Bonjour {recipient_name},\n\n"
            "Votre ticket (réf. {ticket_id}) a été transmis à un superviseur "
            "pour une prise en charge prioritaire.\n"
            "Vous serez contacté dans les plus brefs délais.\n\n"
            "Cordialement,\n"
            "L'équipe Support Client"
        ),
    },
    ('TICKET_ESCALATED', 'SMS'): {
        'subject': 'Ticket escaladé',
        'content': (
            "[Support] Ticket {ticket_id} transmis à un superviseur. "
            "Vous serez contacté très prochainement."
        ),
    },
    ('TICKET_ESCALATED', 'IN_APP'): {
        'subject': 'Ticket escaladé — prise en charge prioritaire',
        'content': (
            "Votre ticket {ticket_id} a été escaladé. "
            "Un superviseur va prendre en charge votre demande."
        ),
    },

    # ---------------------------------------------------------------
    # TICKET_UPDATED
    # ---------------------------------------------------------------
    ('TICKET_UPDATED', 'EMAIL'): {
        'subject': 'Mise à jour du ticket {ticket_id}',
        'content': (
            "Bonjour {recipient_name},\n\n"
            "Votre ticket (réf. {ticket_id}) a été mis à jour par notre équipe.\n"
            "Connectez-vous à votre espace client pour consulter les dernières informations.\n\n"
            "Cordialement,\n"
            "L'équipe Support Client"
        ),
    },
    ('TICKET_UPDATED', 'SMS'): {
        'subject': 'Ticket mis à jour',
        'content': (
            "[Support] Ticket {ticket_id} mis à jour. "
            "Connectez-vous pour consulter les détails."
        ),
    },
    ('TICKET_UPDATED', 'IN_APP'): {
        'subject': 'Ticket mis à jour',
        'content': (
            "Votre ticket {ticket_id} vient d'être mis à jour. "
            "Cliquez pour voir les dernières modifications."
        ),
    },
}


def get_template(notification_type: str, channel: str) -> dict:
    """
    Retourne le dict {'subject': ..., 'content': ...} pour le couple (type, channel).
    Lève ValueError si la combinaison n'est pas définie.
    """
    key = (notification_type, channel)
    if key not in NOTIFICATION_TEMPLATES:
        raise ValueError(
            f"Aucun template défini pour le type '{notification_type}' "
            f"et le canal '{channel}'."
        )
    return NOTIFICATION_TEMPLATES[key]


def render_template(notification_type: str, channel: str, context: dict) -> dict:
    """
    Récupère le template et substitue les variables avec le contexte fourni.

    context attendu :
        ticket_id       → str (UUID du ticket ou "N/A")
        recipient_name  → str (nom ou email du destinataire)
        recipient_email → str

    Retourne {'subject': str, 'content': str} avec les variables remplacées.
    """
    tmpl = get_template(notification_type, channel)
    return {
        'subject': tmpl['subject'].format(**context),
        'content': tmpl['content'].format(**context),
    }
