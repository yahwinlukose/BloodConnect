from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import BloodRequest
import datetime

User = get_user_model()

class BloodRequestAPITests(APITestCase):
    def setUp(self):
        self.list_create_url = '/api/blood-requests/'
        
        self.admin = User.objects.create_user(
            email='admin@example.com', password='pwd', role=User.Role.ADMIN
        )
        self.requester1 = User.objects.create_user(
            email='req1@example.com', password='pwd', role=User.Role.REQUESTER
        )
        self.requester2 = User.objects.create_user(
            email='req2@example.com', password='pwd', role=User.Role.REQUESTER
        )
        self.donor = User.objects.create_user(
            email='donor@example.com', password='pwd', role=User.Role.DONOR
        )
        
        self.valid_payload = {
            'blood_group': 'O+',
            'units_required': 2,
            'hospital_name': 'City Hospital',
            'location': 'Downtown',
            'required_date': (datetime.date.today() + datetime.timedelta(days=2)).isoformat()
        }

    def _get_detail_url(self, pk):
        return f'/api/blood-requests/{pk}/'

    def _create_request(self, user):
        return BloodRequest.objects.create(
            requester=user, 
            blood_group='O+', 
            required_date=datetime.date.today(),
            hospital_name='Test Hospital',
            location='Test Location'
        )

    def test_authenticated_requester_can_create_request(self):
        self.client.force_authenticate(user=self.requester1)
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BloodRequest.objects.count(), 1)

    def test_donor_cannot_create_request(self):
        self.client.force_authenticate(user=self.donor)
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_create_request(self):
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_requester_automatically_assigned(self):
        self.client.force_authenticate(user=self.requester1)
        response = self.client.post(self.list_create_url, self.valid_payload)
        req_obj = BloodRequest.objects.first()
        self.assertEqual(req_obj.requester, self.requester1)

    def test_client_cannot_spoof_requester(self):
        self.client.force_authenticate(user=self.requester1)
        sneaky_payload = self.valid_payload.copy()
        sneaky_payload['requester'] = self.requester2.id
        
        response = self.client.post(self.list_create_url, sneaky_payload)
        req_obj = BloodRequest.objects.first()
        self.assertEqual(req_obj.requester, self.requester1)
        self.assertNotEqual(req_obj.requester, self.requester2)

    def test_authenticated_user_can_list_requests(self):
        self._create_request(self.requester1)
        
        self.client.force_authenticate(user=self.donor)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_requester_can_retrieve_own_request(self):
        req = self._create_request(self.requester1)
        
        self.client.force_authenticate(user=self.requester1)
        response = self.client.get(self._get_detail_url(req.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_requester_cannot_modify_another_users_request(self):
        req = self._create_request(self.requester1)
        
        self.client.force_authenticate(user=self.requester2)
        response = self.client.patch(self._get_detail_url(req.id), {'blood_group': 'A+'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_requester_can_modify_own_request(self):
        req = self._create_request(self.requester1)
        
        self.client.force_authenticate(user=self.requester1)
        response = self.client.patch(self._get_detail_url(req.id), {'blood_group': 'A+'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['blood_group'], 'A+')

    def test_requester_can_cancel_own_request(self):
        req = self._create_request(self.requester1)
        
        self.client.force_authenticate(user=self.requester1)
        response = self.client.patch(self._get_detail_url(req.id), {'status': 'CANCELLED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'CANCELLED')

    def test_donor_cannot_modify_requests(self):
        req = self._create_request(self.requester1)
        
        self.client.force_authenticate(user=self.donor)
        response = self.client.patch(self._get_detail_url(req.id), {'blood_group': 'A+'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_manage_requests(self):
        req = self._create_request(self.requester1)
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(self._get_detail_url(req.id), {'blood_group': 'A+'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        del_response = self.client.delete(self._get_detail_url(req.id))
        self.assertEqual(del_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_blood_group_rejected(self):
        self.client.force_authenticate(user=self.requester1)
        payload = self.valid_payload.copy()
        payload['blood_group'] = 'INVALID'
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_units_rejected(self):
        self.client.force_authenticate(user=self.requester1)
        payload = self.valid_payload.copy()
        payload['units_required'] = 0
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_latitude_rejected(self):
        self.client.force_authenticate(user=self.requester1)
        payload = self.valid_payload.copy()
        payload['latitude'] = 100
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_longitude_rejected(self):
        self.client.force_authenticate(user=self.requester1)
        payload = self.valid_payload.copy()
        payload['longitude'] = 200
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_past_required_date_rejected_when_creating(self):
        self.client.force_authenticate(user=self.requester1)
        payload = self.valid_payload.copy()
        payload['required_date'] = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_existent_request_returns_404(self):
        self.client.force_authenticate(user=self.requester1)
        response = self.client.get(self._get_detail_url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
