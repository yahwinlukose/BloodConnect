from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

"""
This module defines the Notification model for BloodConnect.
Notification stores an application notification.
Firebase delivery is a separate concern.
A notification may exist even if push delivery fails.
Notification records are not proof of medical eligibility or blood availability.
"""

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        BLOOD_REQUEST_MATCH = 'BLOOD_REQUEST_MATCH', _('Blood Request Match')
        MATCH_ACCEPTED = 'MATCH_ACCEPTED', _('Match Accepted')
        MATCH_REJECTED = 'MATCH_REJECTED', _('Match Rejected')
        REQUEST_CANCELLED = 'REQUEST_CANCELLED', _('Request Cancelled')
        REQUEST_FULFILLED = 'REQUEST_FULFILLED', _('Request Fulfilled')
        SYSTEM = 'SYSTEM', _('System')

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    blood_request = models.ForeignKey(
        'blood_requests.BloodRequest',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    donor_matching = models.ForeignKey(
        'matching.DonorMatching',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.BLOOD_REQUEST_MATCH
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['blood_request']),
            models.Index(fields=['donor_matching']),
        ]
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if not self.title:
            raise ValidationError({'title': _('Title is required.')})
        if not self.message:
            raise ValidationError({'message': _('Message is required.')})
            
        if self.read_at and not self.is_read:
            raise ValidationError({'read_at': _('Cannot set read_at if the notification is not marked as read.')})
            
        # "A read notification without read_at should be allowed if we decide read_at may be populated later; document the decision."
        # Decision: We allow is_read=True with read_at=None in case a bulk mark-as-read operation doesn't track timestamps immediately.

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Notification #{self.id or 'New'} - {self.recipient.email} - {self.notification_type}"
