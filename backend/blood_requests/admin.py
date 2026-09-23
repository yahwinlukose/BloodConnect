from django.contrib import admin
from .models import BloodRequest

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'blood_group', 'urgency', 'status', 'hospital_name', 'required_date', 'requester')
    list_filter = ('blood_group', 'status', 'urgency')
    search_fields = ('hospital_name', 'location', 'requester__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('requester', 'blood_group', 'units_required')
        }),
        ('Location Details', {
            'fields': ('hospital_name', 'location', 'latitude', 'longitude')
        }),
        ('Request Status', {
            'fields': ('urgency', 'required_date', 'status', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
