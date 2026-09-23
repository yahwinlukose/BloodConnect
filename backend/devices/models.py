from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class DeviceToken(models.Model):
    class DeviceType(models.TextChoices):
        ANDROID = 'ANDROID', _('Android')
        IOS = 'IOS', _('iOS')
        WEB = 'WEB', _('Web')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens'
    )
    token = models.CharField(
        max_length=255, 
        unique=True,
        help_text=_("FCM Registration Token")
    )
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.ANDROID
    )
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('device token')
        verbose_name_plural = _('device tokens')
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_type']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.device_type} ({'Active' if self.is_active else 'Inactive'})"
