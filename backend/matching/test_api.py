from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from donors.models import DonorProfile
from blood_requests.models import BloodRequest
from matching.models import DonorMatching
import datetime

User = get_user_model()

class MatchingAPITests(APITestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(email='admin@example.com', password='pwd', role=User.Role.ADMIN)
        self.requester1 = User.objects.create_user(email='req1@example.com', password='pwd', role=User.Role.USER)
        self.requester2 = User.objects.create_user(email='req2@example.com', password='pwd', role=User.Role.USER)
        self.donor_user = User.objects.create_user(email='donor@example.com', password='pwd', role=User.Role.USER, first_name='John', last_name='Doe')
        
        # Create a blood request for requester1
        self.blood_request = BloodRequest.objects.create(
            requester=self.requester1,
            blood_group='O+',
            units_required=2,
            hospital_name='City Hospital',
            location='Downtown',
            latitude=10.0,
            longitude=20.0,
            required_date=datetime.date.today() + datetime.timedelta(days=2)
        )
        
        # Create a matching donor
        self.donor_profile = DonorProfile.objects.create(
            user=self.donor_user,
            blood_group='O+',
            date_of_birth=datetime.date(1990, 1, 1),
            gender='MALE',
            location='Uptown',
            latitude=10.05,
            longitude=20.05,
            is_available=True
        )

    def _get_generate_url(self, pk):
        return f'/api/blood-requests/{pk}/matches/generate/'

    def _get_list_url(self, pk):
        return f'/api/blood-requests/{pk}/matches/'

    def test_request_owner_can_generate_matches(self):
        self.client.force_authenticate(user=self.requester1)
        response = self.client.post(self._get_generate_url(self.blood_request.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['donor']['user']['first_name'], 'John')

    def test_request_owner_can_list_matches(self):
        # First generate
        from matching.orchestrator import generate_matches
        generate_matches(self.blood_request)
        
        self.client.force_authenticate(user=self.requester1)
        response = self.client.get(self._get_list_url(self.blood_request.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'PENDING')

    def test_normal_user_cannot_access_another_users_matches(self):
        self.client.force_authenticate(user=self.requester2)
        response = self.client.post(self._get_generate_url(self.blood_request.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # What if it was accessible? BloodRequestViewSet explicitly filters the queryset to only user's requests!
        # So a normal user gets 404 instead of 403. That is perfectly secure.

    def test_admin_can_access_matches(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self._get_generate_url(self.blood_request.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_list = self.client.get(self._get_list_url(self.blood_request.id))
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data), 1)
