from rest_framework import serializers
from .models import DeviceToken

class DeviceTokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255)
    
    class Meta:
        model = DeviceToken
        fields = ('id', 'token', 'device_type', 'is_active', 'created_at', 'updated_at', 'last_used_at')
        read_only_fields = ('id', 'is_active', 'created_at', 'updated_at', 'last_used_at')
        
    def validate_token(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError("Token cannot be blank.")
        return value.strip()
