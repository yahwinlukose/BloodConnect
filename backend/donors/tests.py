from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import DonorProfile
import datetime

User = get_user_model()

class DonorProfileAPITests(APITestCase):
    def setUp(self):
        self.profile_url = reverse('donor_profile')
        
        # Create a user (will act as donor)
        self.donor_user = User.objects.create_user(
            email='donor@example.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            role=User.Role.USER
        )
        
        # Create another user
        self.requester_user = User.objects.create_user(
            email='requester@example.com',
            password='password123',
            first_name='Jane',
            last_name='Smith',
            role=User.Role.USER
        )

        self.valid_payload = {
            'blood_group': 'O+',
            'date_of_birth': '1990-01-01',
            'gender': 'MALE',
            'location': 'Kochi',
            'latitude': '10.0159',
            'longitude': '76.3419',
            'is_available': True
        }

    def test_authenticated_donor_can_create_profile(self):
        self.client.force_authenticate(user=self.donor_user)
        response = self.client.post(self.profile_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DonorProfile.objects.filter(user=self.donor_user).exists())

    def test_unauthenticated_user_cannot_create_profile(self):
        response = self.client.post(self.profile_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_user_cannot_create_second_donor_profile(self):
        self.client.force_authenticate(user=self.donor_user)
        self.client.post(self.profile_url, self.valid_payload)
        
        # Attempt second creation
        response = self.client.post(self.profile_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DonorProfile.objects.filter(user=self.donor_user).count(), 1)

    def test_user_can_retrieve_own_profile(self):
        self.client.force_authenticate(user=self.donor_user)
        self.client.post(self.profile_url, self.valid_payload)
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['blood_group'], 'O+')
        self.assertEqual(response.data['user']['email'], self.donor_user.email)

    def test_user_cannot_retrieve_another_users_profile(self):
        # Create profile for donor 1
        self.client.force_authenticate(user=self.donor_user)
        self.client.post(self.profile_url, self.valid_payload)
        
        # Create donor 2
        donor2 = User.objects.create_user(
            email='donor2@example.com',
            password='password123',
            role=User.Role.USER
        )
        self.client.force_authenticate(user=donor2)
        
        # Donor 2 tries to GET profile (should get 404 because they don't have one, not Donor 1's)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_own_profile(self):
        self.client.force_authenticate(user=self.donor_user)
        self.client.post(self.profile_url, self.valid_payload)
        
        patch_payload = {'blood_group': 'A-', 'is_available': False}
        response = self.client.patch(self.profile_url, patch_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['blood_group'], 'A-')
        self.assertFalse(response.data['is_available'])

    def test_future_date_of_birth_is_rejected(self):
        self.client.force_authenticate(user=self.donor_user)
        invalid_payload = self.valid_payload.copy()
        future_date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        invalid_payload['date_of_birth'] = future_date
        
        response = self.client.post(self.profile_url, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date_of_birth', response.data)

    def test_future_last_donation_date_is_rejected(self):
        self.client.force_authenticate(user=self.donor_user)
        invalid_payload = self.valid_payload.copy()
        future_date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        invalid_payload['last_donation_date'] = future_date
        
        response = self.client.post(self.profile_url, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_donation_date', response.data)

    def test_invalid_latitude_is_rejected(self):
        self.client.force_authenticate(user=self.donor_user)
        invalid_payload = self.valid_payload.copy()
        invalid_payload['latitude'] = '95.0'
        
        response = self.client.post(self.profile_url, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('latitude', response.data)

    def test_invalid_longitude_is_rejected(self):
        self.client.force_authenticate(user=self.donor_user)
        invalid_payload = self.valid_payload.copy()
        invalid_payload['longitude'] = '-185.0'
        
        response = self.client.post(self.profile_url, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('longitude', response.data)

    def test_user_field_cannot_be_overridden_by_client(self):
        self.client.force_authenticate(user=self.donor_user)
        sneaky_payload = self.valid_payload.copy()
        sneaky_payload['user'] = self.requester_user.id
        
        response = self.client.post(self.profile_url, sneaky_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify it was created for donor_user, NOT requester_user
        self.assertTrue(DonorProfile.objects.filter(user=self.donor_user).exists())
        self.assertFalse(DonorProfile.objects.filter(user=self.requester_user).exists())
        self.assertEqual(response.data['user']['email'], self.donor_user.email)
