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
            email='req1@example.com', password='pwd', role=User.Role.USER
        )
        self.requester2 = User.objects.create_user(
            email='req2@example.com', password='pwd', role=User.Role.USER
        )
        self.donor = User.objects.create_user(
            email='donor@example.com', password='pwd', role=User.Role.USER
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

    def test_normal_user_cannot_see_others_requests(self):
        self._create_request(self.requester1)

        self.client.force_authenticate(user=self.donor)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_normal_user_can_see_own_requests(self):
        self._create_request(self.requester1)

        self.client.force_authenticate(user=self.requester1)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_see_all_requests(self):
        self._create_request(self.requester1)

        self.client.force_authenticate(user=self.admin)
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

from matching.models import DonorMatching
from donors.models import DonorProfile

class BloodRequestMatchingIntegrationTests(APITestCase):
    def setUp(self):
        self.list_create_url = '/api/blood-requests/'
        self.requester = User.objects.create_user(
            email='req_integration@example.com', password='pwd', role=User.Role.USER
        )
        self.valid_payload = {
            'blood_group': 'O+',
            'units_required': 1,
            'hospital_name': 'H',
            'location': 'L',
            'required_date': (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
            'latitude': 0.0,
            'longitude': 0.0,
            'urgency': 'NORMAL'
        }

    def _create_donor(self, email, blood_group, lat=0.0, lon=0.0, is_available=True):
        u = User.objects.create_user(email=email, password='pwd', role=User.Role.USER)
        return DonorProfile.objects.create(
            user=u,
            blood_group=blood_group,
            date_of_birth=datetime.date(1990, 1, 1),
            gender=DonorProfile.Gender.MALE,
            latitude=lat,
            longitude=lon,
            is_available=is_available
        )

    def test_creating_request_creates_compatible_match(self):
        self._create_donor('d1@e.com', 'O+')
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DonorMatching.objects.count(), 1)
        self.assertEqual(DonorMatching.objects.first().donor.user.email, 'd1@e.com')

    def test_incompatible_donor_no_match(self):
        self._create_donor('d1@e.com', 'AB+')
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DonorMatching.objects.count(), 0)

    def test_unavailable_donor_no_match(self):
        self._create_donor('d1@e.com', 'O+', is_available=False)
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DonorMatching.objects.count(), 0)

    def test_duplicate_generation_no_duplicates(self):
        self._create_donor('d1@e.com', 'O+')
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DonorMatching.objects.count(), 1)

        req_id = response.data['id']
        gen_url = f'/api/blood-requests/{req_id}/matches/generate/'
        response2 = self.client.post(gen_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(DonorMatching.objects.count(), 1)

    def test_existing_accepted_preserved(self):
        self._create_donor('d1@e.com', 'O+')
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        match = DonorMatching.objects.first()
        match.status = DonorMatching.Status.ACCEPTED
        match.save()

        req_id = response.data['id']
        gen_url = f'/api/blood-requests/{req_id}/matches/generate/'
        self.client.post(gen_url)

        match.refresh_from_db()
        self.assertEqual(match.status, DonorMatching.Status.ACCEPTED)

    def test_create_request_zero_eligible_donors(self):
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DonorMatching.objects.count(), 0)
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from donors.models import DonorProfile
from matching.models import DonorMatching
from blood_requests.models import BloodRequest
import datetime

User = get_user_model()

class BloodRequestViewIntegrationTests(APITestCase):
    def setUp(self):
        self.list_create_url = '/api/blood-requests/'
        self.requester = User.objects.create_user(
            email='req_view@example.com', password='pwd', role=User.Role.USER
        )
        self.valid_payload = {
            'blood_group': 'O+',
            'units_required': 1,
            'hospital_name': 'Amala hospital',
            'location': 'aluva',
            'required_date': (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
            'latitude': 0.0,
            'longitude': 0.0,
            'urgency': 'CRITICAL'
        }

    def _create_donor(self, email, blood_group, lat=10.015900, lon=76.341900, is_available=True):
        u = User.objects.create_user(email=email, password='pwd', role=User.Role.USER)
        return DonorProfile.objects.create(
            user=u,
            blood_group=blood_group,
            date_of_birth=datetime.date(2000, 1, 15),
            gender=DonorProfile.Gender.MALE,
            latitude=lat,
            longitude=lon,
            is_available=is_available
        )

    def test_view_post_creates_match_real_distance(self):
        self._create_donor('d1_real@e.com', 'O+')
        self.client.force_authenticate(user=self.requester)

        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        req_id = response.data['id']
        matches = DonorMatching.objects.filter(blood_request_id=req_id)
        self.assertTrue(matches.exists())
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from donors.models import DonorProfile
from matching.models import DonorMatching
from blood_requests.models import BloodRequest
import datetime

User = get_user_model()

class BloodRequestTransactionTests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_create_url = '/api/blood-requests/'
        self.requester = User.objects.create_user(
            email='req_trans@example.com', password='pwd', role=User.Role.USER
        )
        self.valid_payload = {
            'blood_group': 'O+',
            'units_required': 1,
            'hospital_name': 'Amala hospital',
            'location': 'aluva',
            'required_date': (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
            'latitude': 0.0,
            'longitude': 0.0,
            'urgency': 'CRITICAL'
        }

    def _create_donor(self, email, blood_group, lat=10.015900, lon=76.341900, is_available=True):
        u = User.objects.create_user(email=email, password='pwd', role=User.Role.USER)
        return DonorProfile.objects.create(
            user=u,
            blood_group=blood_group,
            date_of_birth=datetime.date(2000, 1, 15),
            gender=DonorProfile.Gender.MALE,
            latitude=lat,
            longitude=lon,
            is_available=is_available
        )

    def test_view_post_creates_match_without_transaction(self):
        self._create_donor('d1_trans@e.com', 'O+')
        self.client.force_authenticate(user=self.requester)

        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        req_id = response.data['id']
        matches = DonorMatching.objects.filter(blood_request_id=req_id)
        self.assertTrue(matches.exists(), f"No matches found! Matches count: {matches.count()}")
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from donors.models import DonorProfile
from matching.models import DonorMatching
from blood_requests.models import BloodRequest
import datetime

User = get_user_model()

class BloodRequestDebugTests(APITestCase):
    def setUp(self):
        self.list_create_url = '/api/blood-requests/'
        self.requester = User.objects.create_user(
            email='req_debug@example.com', password='pwd', role=User.Role.USER
        )
        self.valid_payload = {
            'blood_group': 'O+',
            'units_required': 1,
            'hospital_name': 'Amala hospital',
            'location': 'aluva',
            'required_date': (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
            'latitude': 0.0,
            'longitude': 0.0,
            'urgency': 'CRITICAL'
        }

    def _create_donor(self, email, blood_group, lat=10.015900, lon=76.341900, is_available=True):
        u = User.objects.create_user(email=email, password='pwd', role=User.Role.USER)
        return DonorProfile.objects.create(
            user=u,
            blood_group=blood_group,
            date_of_birth=datetime.date(2000, 1, 15),
            gender=DonorProfile.Gender.MALE,
            latitude=lat,
            longitude=lon,
            is_available=is_available
        )

    def test_view_post_creates_match_debug(self):
        self._create_donor('d1_debug@e.com', 'O+')
        self.client.force_authenticate(user=self.requester)

        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        req_id = response.data['id']
        matches = list(DonorMatching.objects.filter(blood_request_id=req_id))
        print("Matches found:", matches)
        self.assertTrue(len(matches) > 0)
