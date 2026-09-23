from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime

class BloodRequest(models.Model):
    class BloodGroup(models.TextChoices):
        A_POS = 'A+', _('A+')
        A_NEG = 'A-', _('A-')
        B_POS = 'B+', _('B+')
        B_NEG = 'B-', _('B-')
        AB_POS = 'AB+', _('AB+')
        AB_NEG = 'AB-', _('AB-')
        O_POS = 'O+', _('O+')
        O_NEG = 'O-', _('O-')

    class Urgency(models.TextChoices):
        NORMAL = 'NORMAL', _('Normal')
        URGENT = 'URGENT', _('Urgent')
        CRITICAL = 'CRITICAL', _('Critical')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        MATCHING = 'MATCHING', _('Matching')
        FULFILLED = 'FULFILLED', _('Fulfilled')
        CANCELLED = 'CANCELLED', _('Cancelled')

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blood_requests'
    )
    blood_group = models.CharField(
        max_length=3,
        choices=BloodGroup.choices,
    )
    units_required = models.PositiveIntegerField(default=1)
    hospital_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    urgency = models.CharField(
        max_length=10,
        choices=Urgency.choices,
        default=Urgency.NORMAL
    )
    required_date = models.DateField()
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('blood request')
        verbose_name_plural = _('blood requests')
        indexes = [
            models.Index(fields=['blood_group']),
            models.Index(fields=['status']),
            models.Index(fields=['urgency']),
            models.Index(fields=['required_date']),
            models.Index(fields=['requester']),
        ]

    def clean(self):
        super().clean()
        
        # Validation for units_required
        if self.units_required is not None and self.units_required < 1:
            raise ValidationError({'units_required': _('Units required must be at least 1.')})
            
        # Validation for latitude
        if self.latitude is not None and (self.latitude < -90 or self.latitude > 90):
            raise ValidationError({'latitude': _('Latitude must be between -90 and 90.')})
            
        # Validation for longitude
        if self.longitude is not None and (self.longitude < -180 or self.longitude > 180):
            raise ValidationError({'longitude': _('Longitude must be between -180 and 180.')})
            
        # Validation for required_date (only on creation)
        if not self.pk and self.required_date and self.required_date < datetime.date.today():
            raise ValidationError({'required_date': _('Required date cannot be in the past when creating a request.')})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Blood Request #{self.id} - {self.blood_group} - {self.status}"
