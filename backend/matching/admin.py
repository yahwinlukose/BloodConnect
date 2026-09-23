from django.contrib import admin
from .models import DonorMatching

@admin.register(DonorMatching)
class DonorMatchingAdmin(admin.ModelAdmin):
    list_display = ('id', 'blood_request', 'donor', 'distance_km', 'match_score', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('blood_request__id', 'donor__user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('blood_request', 'donor')
        }),
        ('Match Details', {
            'fields': ('distance_km', 'match_score', 'status', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
