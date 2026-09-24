from rest_framework import serializers
from .models import DonorMatching
from donors.models import DonorProfile
from django.contrib.auth import get_user_model

class MatchDonorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name')
        read_only_fields = fields

class MatchDonorProfileSerializer(serializers.ModelSerializer):
    user = MatchDonorUserSerializer(read_only=True)

    class Meta:
        model = DonorProfile
        fields = ('id', 'user', 'blood_group', 'gender', 'location', 'is_available')
        read_only_fields = fields

class DonorMatchingSerializer(serializers.ModelSerializer):
    donor = MatchDonorProfileSerializer(read_only=True)

    class Meta:
        model = DonorMatching
        fields = ('id', 'donor', 'distance_km', 'match_score', 'status')
        read_only_fields = fields

class BloodRequestForDonorSerializer(serializers.ModelSerializer):
    class Meta:
        from blood_requests.models import BloodRequest
        model = BloodRequest
        fields = (
            'id', 'blood_group', 'units_required', 'hospital_name',
            'location', 'latitude', 'longitude', 'urgency',
            'required_date', 'description'
        )
        read_only_fields = fields

class DonorMatchForDonorSerializer(serializers.ModelSerializer):
    blood_request = BloodRequestForDonorSerializer(read_only=True)

    class Meta:
        model = DonorMatching
        fields = ('id', 'blood_request', 'distance_km', 'match_score', 'status', 'created_at', 'responded_at')
        read_only_fields = fields
