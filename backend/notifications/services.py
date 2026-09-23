from django.db import transaction
from .models import Notification
from matching.models import DonorMatching

"""
This module provides services for creating persistent application notifications.
It does not deliver push notifications.
Delivery will be handled later by a separate Firebase/FCM service.
A persistent notification can exist even when push delivery fails.
The notification does not constitute medical or clinical approval.
"""

def _generate_match_notification_title() -> str:
    """Generate the title for a match notification."""
    return "Blood request match"

def _generate_match_notification_message(blood_request) -> str:
    """Generate the message body for a match notification."""
    group_display = blood_request.get_blood_group_display()
    urgency_display = blood_request.get_urgency_display()
    
    return (
        f"An {group_display} blood request for {blood_request.units_required} "
        f"unit(s) is needed at {blood_request.hospital_name}, {blood_request.location}. "
        f"Urgency: {urgency_display}."
    )

@transaction.atomic
def create_match_notification(donor_matching: DonorMatching) -> Notification | None:
    """
    Creates a persistent Notification for a donor when a DonorMatching 
    represents an eligible pending match.
    
    Returns:
        The created or existing Notification, or None if the match is not PENDING.
    """
    if donor_matching.status != DonorMatching.Status.PENDING:
        return None

    blood_request = donor_matching.blood_request
    recipient = donor_matching.donor.user

    notification, created = Notification.objects.get_or_create(
        donor_matching=donor_matching,
        notification_type=Notification.NotificationType.BLOOD_REQUEST_MATCH,
        defaults={
            'recipient': recipient,
            'blood_request': blood_request,
            'title': _generate_match_notification_title(),
            'message': _generate_match_notification_message(blood_request)
        }
    )

    return notification
