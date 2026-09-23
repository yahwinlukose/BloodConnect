from django.contrib import admin
from .models import DeviceToken

@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_preview', 'device_type', 'is_active', 'created_at', 'last_used_at')
    list_filter = ('device_type', 'is_active', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'token')
    readonly_fields = ('created_at', 'updated_at', 'last_used_at')
    
    def token_preview(self, obj):
        if len(obj.token) > 20:
            return f"{obj.token[:17]}..."
        return obj.token
    token_preview.short_description = 'Token'
