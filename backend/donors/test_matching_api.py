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
        # Initial status should be PENDING
        self.assertEqual(self.req1.status, BloodRequest.Status.PENDING)

        self.client.force_authenticate(user=self.user1)
        res = self.client.post(f'/api/donors/matches/{self.match1.id}/accept/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.match1.refresh_from_db()
        self.assertEqual(self.match1.status, DonorMatching.Status.ACCEPTED)
        self.assertIsNotNone(self.match1.responded_at)

        # 1. Pending request + donor accepts -> matching becomes ACCEPTED and request becomes MATCHING.
        # 2. Donor acceptance does not make the request FULFILLED.
        self.req1.refresh_from_db()
        self.assertEqual(self.req1.status, BloodRequest.Status.MATCHING)
        self.assertNotEqual(self.req1.status, BloodRequest.Status.FULFILLED)

        # 3. Multiple units still remain represented correctly (units_required was 2).
        self.assertEqual(self.req1.units_required, 2)

    def test_donor_acceptance_preserves_existing_request_status(self):
        # Set the request to something other than PENDING
        self.req1.status = BloodRequest.Status.FULFILLED
        self.req1.save()

        self.client.force_authenticate(user=self.user1)
        res = self.client.post(f'/api/donors/matches/{self.match1.id}/accept/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.req1.refresh_from_db()
        self.assertEqual(self.req1.status, BloodRequest.Status.FULFILLED)

    def test_donor_rejects_own_match(self):
        # 4. Existing accepted/rejected behavior remains intact.
        self.client.force_authenticate(user=self.user2)
        res = self.client.post(f'/api/donors/matches/{self.match2.id}/reject/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.match2.refresh_from_db()
        self.assertEqual(self.match2.status, DonorMatching.Status.REJECTED)
        self.assertIsNotNone(self.match2.responded_at)

        # Request status should remain PENDING
        self.req1.refresh_from_db()
        self.assertEqual(self.req1.status, BloodRequest.Status.PENDING)

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


class RetroactiveMatchingOnDonorProfileSaveTests(TestCase):
    """
    Tests for the post_save signal on DonorProfile that triggers retroactive
    matching against all active BloodRequests.
    """

    def setUp(self):
        self.today = datetime.date.today()
        self.requester = User.objects.create_user(
            email="retro_requester@test.com", password="password"
        )
        # A pre-existing active blood request for O+
        self.active_request = BloodRequest.objects.create(
            requester=self.requester,
            blood_group="O+",
            units_required=1,
            hospital_name="Retro Hospital",
            location="Retro Location",
            latitude=10.0,
            longitude=10.0,
            urgency=BloodRequest.Urgency.NORMAL,
            required_date=self.today + datetime.timedelta(days=2),
            status=BloodRequest.Status.PENDING,
        )

    def _create_user(self, email):
        return User.objects.create_user(email=email, password="password")

    # ------------------------------------------------------------------
    # Test 1: Blood request exists BEFORE donor profile creation
    # ------------------------------------------------------------------
    def test_creating_donor_profile_matches_pre_existing_request(self):
        """
        When a compatible, eligible DonorProfile is created after an active
        BloodRequest already exists, a DonorMatching record must be created.
        """
        donor_user = self._create_user("retro_donor_create@test.com")
        DonorProfile.objects.create(
            user=donor_user,
            blood_group="O+",
            date_of_birth=datetime.date(1990, 1, 1),
            gender="MALE",
            latitude=10.0,
            longitude=10.0,
            is_available=True,
        )

        self.assertEqual(
            DonorMatching.objects.filter(blood_request=self.active_request).count(),
            1,
        )

    # ------------------------------------------------------------------
    # Test 2: Donor profile exists BEFORE blood request creation (existing behaviour)
    # ------------------------------------------------------------------
    def test_orchestrator_matches_pre_existing_donor_profile_to_new_request(self):
        """
        When generate_matches() is called for a new BloodRequest and a compatible,
        eligible DonorProfile already exists, a DonorMatching record is created.
        This verifies the orchestrator's pre-existing behaviour is unbroken by the
        new signal.
        """
        donor_user = self._create_user("retro_donor_existing@test.com")
        donor_profile = DonorProfile.objects.create(
            user=donor_user,
            blood_group="O+",
            date_of_birth=datetime.date(1990, 1, 1),
            gender="MALE",
            latitude=10.0,
            longitude=10.0,
            is_available=True,
        )

        # A new blood request is created after the donor profile exists.
        # In production this goes through BloodRequestViewSet.perform_create()
        # which calls generate_matches(). We call it directly here to test the
        # orchestrator layer in isolation from the ViewSet.
        from matching.orchestrator import generate_matches

        new_request = BloodRequest.objects.create(
            requester=self.requester,
            blood_group="O+",
            units_required=1,
            hospital_name="New Hospital",
            location="New Location",
            latitude=10.0,
            longitude=10.0,
            urgency=BloodRequest.Urgency.NORMAL,
            required_date=self.today + datetime.timedelta(days=3),
            status=BloodRequest.Status.PENDING,
        )
        generate_matches(new_request)

        self.assertTrue(
            DonorMatching.objects.filter(
                blood_request=new_request, donor=donor_profile
            ).exists()
        )

    # ------------------------------------------------------------------
    # Test 3: Ineligible donor → no match
    # ------------------------------------------------------------------
    def test_ineligible_donor_not_matched_on_profile_create(self):
        """
        A donor whose last_donation_date is within 90 days must not be matched
        even when their profile is created after an active request exists.
        """
        donor_user = self._create_user("retro_ineligible@test.com")
        recent_donation = self.today - datetime.timedelta(days=30)
        DonorProfile.objects.create(
            user=donor_user,
            blood_group="O+",
            date_of_birth=datetime.date(1990, 1, 1),
            gender="MALE",
            is_available=True,
            last_donation_date=recent_donation,
        )

        self.assertEqual(
            DonorMatching.objects.filter(blood_request=self.active_request).count(),
            0,
        )

    # ------------------------------------------------------------------
    # Test 4: Updating donor profile doesn't create duplicate matches
    # ------------------------------------------------------------------
    def test_updating_donor_profile_does_not_create_duplicate_matches(self):
        """
        Repeated DonorProfile saves (e.g. location updates) must not create
        additional DonorMatching rows for the same (blood_request, donor) pair.
        """
        donor_user = self._create_user("retro_update@test.com")
        profile = DonorProfile.objects.create(
            user=donor_user,
            blood_group="O+",
            date_of_birth=datetime.date(1990, 1, 1),
            gender="MALE",
            latitude=10.0,
            longitude=10.0,
            is_available=True,
        )

        self.assertEqual(
            DonorMatching.objects.filter(blood_request=self.active_request).count(),
            1,
        )

        # Update the profile twice more
        profile.location = "New Location"
        profile.save()
        profile.latitude = 10.05
        profile.save()

        # Still exactly one DonorMatching record
        self.assertEqual(
            DonorMatching.objects.filter(blood_request=self.active_request).count(),
            1,
        )

    # ------------------------------------------------------------------
    # Test 5: Existing ACCEPTED / REJECTED status is preserved on profile update
    # ------------------------------------------------------------------
    def test_accepted_and_rejected_match_statuses_preserved_on_profile_update(self):
        """
        When a DonorProfile is updated, generate_matches() must not overwrite
        ACCEPTED or REJECTED DonorMatching statuses.
        """
        # Donor A – compatible, will be matched and then ACCEPTED
        user_a = self._create_user("retro_accepted@test.com")
        profile_a = DonorProfile.objects.create(
            user=user_a,
            blood_group="O+",
            date_of_birth=datetime.date(1990, 1, 1),
            gender="MALE",
            latitude=10.0,
            longitude=10.0,
            is_available=True,
        )

        # Donor B – compatible, will be matched and then REJECTED
        user_b = self._create_user("retro_rejected@test.com")
        profile_b = DonorProfile.objects.create(
            user=user_b,
            blood_group="O+",
            date_of_birth=datetime.date(1990, 1, 1),
            gender="MALE",
            latitude=10.0,
            longitude=10.0,
            is_available=True,
        )

        match_a = DonorMatching.objects.get(
            blood_request=self.active_request, donor=profile_a
        )
        match_a.status = DonorMatching.Status.ACCEPTED
        match_a.save()

        match_b = DonorMatching.objects.get(
            blood_request=self.active_request, donor=profile_b
        )
        match_b.status = DonorMatching.Status.REJECTED
        match_b.save()

        # Now trigger another profile save (simulates a profile update)
        profile_a.location = "Updated Location"
        profile_a.save()

        match_a.refresh_from_db()
        match_b.refresh_from_db()

        self.assertEqual(match_a.status, DonorMatching.Status.ACCEPTED)
        self.assertEqual(match_b.status, DonorMatching.Status.REJECTED)
