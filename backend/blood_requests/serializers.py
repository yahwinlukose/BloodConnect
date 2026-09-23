from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BloodRequest
import datetime

User = get_user_model()

class RequesterMinimalSerializer(serializers.ModelSerializer):
    """Safe representation of the requester."""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')
        read_only_fields = fields

class BloodRequestSerializer(serializers.ModelSerializer):
    requester = RequesterMinimalSerializer(read_only=True)

    class Meta:
        model = BloodRequest
        fields = (
            'id', 'requester', 'blood_group', 'units_required',
            'hospital_name', 'location', 'latitude', 'longitude',
            'urgency', 'required_date', 'description', 'status',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'requester', 'created_at', 'updated_at')

    def validate_units_required(self, value):
        if value < 1:
            raise serializers.ValidationError("Units required must be at least 1.")
        return value

    def validate_latitude(self, value):
        if value is not None and (value < -90 or value > 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if value is not None and (value < -180 or value > 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value

    def validate_required_date(self, value):
        # We only prevent past dates for newly created requests.
        # If the instance already exists (e.g., during a PATCH), we allow the date to remain in the past
        # unless they are explicitly modifying it to a past date (which we generally should prevent, 
        # but the core requirement is "cannot be in the past for newly created requests").
        if self.instance is None and value < datetime.date.today():
            raise serializers.ValidationError("Required date cannot be in the past when creating a request.")
        return value
