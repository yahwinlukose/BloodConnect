from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import DonorProfile
import datetime

User = get_user_model()

class MinimalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')
        read_only_fields = fields

class DonorProfileSerializer(serializers.ModelSerializer):
    user = MinimalUserSerializer(read_only=True)

    class Meta:
        model = DonorProfile
        fields = (
            'id', 'user', 'blood_group', 'date_of_birth', 'gender',
            'location', 'latitude', 'longitude', 'is_available',
            'last_donation_date', 'created_at', 'updated_at'
        )
        read_only_fields = ('user', 'created_at', 'updated_at')

    def validate_date_of_birth(self, value):
        if value > datetime.date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_last_donation_date(self, value):
        if value and value > datetime.date.today():
            raise serializers.ValidationError("Last donation date cannot be in the future.")
        return value

    def validate_latitude(self, value):
        if value is not None and (value < -90 or value > 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if value is not None and (value < -180 or value > 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value
