from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from blood_requests.models import BloodRequest
from donors.models import DonorProfile
from matching.models import DonorMatching
import datetime

User = get_user_model()

class DonorMatchingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # User 1 with Donor Profile
        self.user1 = User.objects.create_user(email="donor1@test.com", password="password")
        self.donor1 = DonorProfile.objects.create(
            user=self.user1,
            blood_group="O+",
            date_of_birth=datetime.date(1990, 1, 1),
            gender="MALE",
            location="Test Location 1",
            latitude=10.0,
            longitude=10.0,
            is_available=True
        )

        # User 2 with Donor Profile
        self.user2 = User.objects.create_user(email="donor2@test.com", password="password")
        self.donor2 = DonorProfile.objects.create(
            user=self.user2,
            blood_group="O-",
            date_of_birth=datetime.date(1995, 1, 1),
            gender="FEMALE",
            location="Test Location 2",
            latitude=20.0,
            longitude=20.0,
            is_available=True
        )

        # User 3 without Donor Profile
        self.user3 = User.objects.create_user(email="nodonor@test.com", password="password")

        # Requester
        self.requester = User.objects.create_user(email="requester@test.com", password="password")

        # Blood Request 1 (Active)
        self.req1 = BloodRequest.objects.create(
            requester=self.requester,
            blood_group="O+",
            units_required=2,
            hospital_name="Hospital A",
            location="Location A",
            latitude=10.0,
            longitude=10.0,
            urgency=BloodRequest.Urgency.NORMAL,
            required_date=datetime.date.today(),
            status=BloodRequest.Status.PENDING
        )

        # Blood Request 2 (Fulfilled - not active for matching)
        self.req2 = BloodRequest.objects.create(
            requester=self.requester,
            blood_group="A+",
            units_required=1,
            hospital_name="Hospital B",
            location="Location B",
            urgency=BloodRequest.Urgency.NORMAL,
            required_date=datetime.date.today(),
            status=BloodRequest.Status.FULFILLED
        )

        # Match for donor 1
        self.match1 = DonorMatching.objects.create(
            blood_request=self.req1,
            donor=self.donor1,
            distance_km=0.00,
            match_score=100.00,
            status=DonorMatching.Status.PENDING
        )

        # Match for donor 2
        self.match2 = DonorMatching.objects.create(
            blood_request=self.req1,
            donor=self.donor2,
            distance_km=15.50,
            match_score=80.00,
            status=DonorMatching.Status.PENDING
        )

        # Match for donor 1 on inactive request
        self.match3 = DonorMatching.objects.create(
            blood_request=self.req2,
            donor=self.donor1,
            status=DonorMatching.Status.PENDING
        )

    def test_unauthenticated_requests_rejected(self):
        res = self.client.get('/api/donors/matches/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.post(f'/api/donors/matches/{self.match1.id}/accept/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_without_donor_profile_rejected(self):
        self.client.force_authenticate(user=self.user3)
        res = self.client.get('/api/donors/matches/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.post(f'/api/donors/matches/{self.match1.id}/accept/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_donor_views_relevant_matches(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.get('/api/donors/matches/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.json()
        # Should only see match1 (active request), not match3 (inactive request)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], self.match1.id)

        # Check that distance is returned correctly
        self.assertEqual(data[0]['distance_km'], '0.00')
        self.assertEqual(data[0]['match_score'], '100.00')

        # Check nested blood request data
        self.assertEqual(data[0]['blood_request']['hospital_name'], "Hospital A")

    def test_donor_accepts_own_match(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.post(f'/api/donors/matches/{self.match1.id}/accept/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.match1.refresh_from_db()
        self.assertEqual(self.match1.status, DonorMatching.Status.ACCEPTED)
        self.assertIsNotNone(self.match1.responded_at)

    def test_donor_rejects_own_match(self):
        self.client.force_authenticate(user=self.user2)
        res = self.client.post(f'/api/donors/matches/{self.match2.id}/reject/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.match2.refresh_from_db()
        self.assertEqual(self.match2.status, DonorMatching.Status.REJECTED)
        self.assertIsNotNone(self.match2.responded_at)

    def test_donor_cannot_modify_another_donors_match(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.post(f'/api/donors/matches/{self.match2.id}/accept/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_state_transitions_rejected(self):
        # First transition to ACCEPTED
        self.client.force_authenticate(user=self.user1)
        res = self.client.post(f'/api/donors/matches/{self.match1.id}/accept/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Try to transition again (e.g. to REJECTED) from ACCEPTED
        res = self.client.post(f'/api/donors/matches/{self.match1.id}/reject/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        self.match1.refresh_from_db()
        self.assertEqual(self.match1.status, DonorMatching.Status.ACCEPTED)
