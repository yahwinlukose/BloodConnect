from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class DonorMatching(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        NOTIFIED = 'NOTIFIED', _('Notified')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')
        EXPIRED = 'EXPIRED', _('Expired')
        CANCELLED = 'CANCELLED', _('Cancelled')

    blood_request = models.ForeignKey(
        'blood_requests.BloodRequest',
        on_delete=models.CASCADE,
        related_name='matches'
    )
    donor = models.ForeignKey(
        'donors.DonorProfile',
        on_delete=models.CASCADE,
        related_name='matches'
    )
    distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('donor matching')
        verbose_name_plural = _('donor matchings')
        constraints = [
            models.UniqueConstraint(
                fields=['blood_request', 'donor'],
                name='unique_blood_request_donor_match'
            )
        ]
        indexes = [
            models.Index(fields=['blood_request']),
            models.Index(fields=['donor']),
            models.Index(fields=['status']),
        ]

    def clean(self):
        super().clean()
        if self.distance_km is not None and self.distance_km < 0:
            raise ValidationError({'distance_km': _('Distance cannot be negative.')})
        if self.match_score is not None:
            if self.match_score < 0:
                raise ValidationError({'match_score': _('Match score cannot be negative.')})
            if self.match_score > 100:
                raise ValidationError({'match_score': _('Match score cannot exceed 100.')})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        # Using self.blood_request_id directly avoids an extra DB query if the related object isn't loaded
        return f"Match #{self.id} - Request #{self.blood_request_id} - {self.donor} - {self.status}"
