from django.contrib import admin
from .models import DonorProfile

@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'is_available', 'gender', 'date_of_birth', 'last_donation_date')
    list_filter = ('blood_group', 'is_available', 'gender')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'blood_group', 'gender', 'date_of_birth')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Donation Status', {
            'fields': ('is_available', 'last_donation_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
