from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class DonorProfile(models.Model):
    class BloodGroup(models.TextChoices):
        A_POS = 'A+', _('A+')
        A_NEG = 'A-', _('A-')
        B_POS = 'B+', _('B+')
        B_NEG = 'B-', _('B-')
        AB_POS = 'AB+', _('AB+')
        AB_NEG = 'AB-', _('AB-')
        O_POS = 'O+', _('O+')
        O_NEG = 'O-', _('O-')

    class Gender(models.TextChoices):
        MALE = 'MALE', _('Male')
        FEMALE = 'FEMALE', _('Female')
        OTHER = 'OTHER', _('Other')
        PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY', _('Prefer not to say')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='donor_profile'
    )
    blood_group = models.CharField(
        max_length=3,
        choices=BloodGroup.choices,
    )
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
    )
    location = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text=_("Latitude coordinate")
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text=_("Longitude coordinate")
    )
    is_available = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('donor profile')
        verbose_name_plural = _('donor profiles')
        indexes = [
            models.Index(fields=['blood_group']),
            models.Index(fields=['is_available']),
            models.Index(fields=['blood_group', 'is_available']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.blood_group})"
