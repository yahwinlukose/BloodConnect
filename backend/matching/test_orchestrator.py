from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from unittest.mock import patch
from donors.models import DonorProfile
from blood_requests.models import BloodRequest
from matching.models import DonorMatching
from matching.orchestrator import generate_matches
import datetime

User = get_user_model()

class OrchestratorTests(TestCase):
    def setUp(self):
        self.requester_user = User.objects.create_user(
            email='req@example.com', password='pwd', role=User.Role.USER
        )
        self.today = datetime.date.today()
        self.blood_request = BloodRequest.objects.create(
            requester=self.requester_user,
            blood_group=BloodRequest.BloodGroup.O_POS,
            units_required=1,
            hospital_name='Test Hospital',
            location='Test Location',
            latitude=0.0,
            longitude=0.0,
            required_date=self.today + datetime.timedelta(days=1),
            urgency=BloodRequest.Urgency.NORMAL
        )

    def _create_donor(self, email, blood_group, lat=None, lon=None):
        u = User.objects.create_user(email=email, password='pwd', role=User.Role.USER)
        return DonorProfile.objects.create(
            user=u,
            blood_group=blood_group,
            date_of_birth=datetime.date(1990, 1, 1),
            gender=DonorProfile.Gender.MALE,
            latitude=lat,
            longitude=lon
        )

    def test_generates_correct_matches_for_multiple_donors(self):
        # 1. Generates matches for eligible donors.
        # 8. Multiple eligible donors create multiple matches.
        d1 = self._create_donor('d1@e.com', 'O-', lat=1.0, lon=0.0)
        d2 = self._create_donor('d2@e.com', 'O+', lat=0.1, lon=0.0)
        
        matches = generate_matches(self.blood_request)
        self.assertEqual(matches.count(), 2)
        
        # 2. Correct blood_request is stored.
        # 3. Correct donor is stored.
        # 4. Correct distance is stored.
        # 5. Correct score is stored.
        # 6. New matches have PENDING status.
        # 7. responded_at starts as NULL.
        match_d1 = matches.get(donor=d1)
        self.assertEqual(match_d1.blood_request, self.blood_request)
        self.assertEqual(match_d1.status, DonorMatching.Status.PENDING)
        self.assertIsNone(match_d1.responded_at)
        self.assertIsNotNone(match_d1.distance_km)
        self.assertIsNotNone(match_d1.match_score)
        
        match_d2 = matches.get(donor=d2)
        self.assertEqual(match_d2.blood_request, self.blood_request)
        
    def test_no_eligible_donors_creates_zero_matches(self):
        # 9. No eligible donors creates zero matches.
        matches = generate_matches(self.blood_request)
        self.assertEqual(matches.count(), 0)

    def test_idempotency_no_duplicates(self):
        # 10. Running generate_matches() twice does not create duplicates.
        self._create_donor('d1@e.com', 'O+')
        generate_matches(self.blood_request)
        self.assertEqual(DonorMatching.objects.count(), 1)
        
        generate_matches(self.blood_request)
        self.assertEqual(DonorMatching.objects.count(), 1)

    def test_pending_match_updates_values(self):
        # 11. Existing PENDING match gets updated distance/score if values change.
        d1 = self._create_donor('d1@e.com', 'O+', lat=0.1, lon=0.0)
        generate_matches(self.blood_request)
        match = DonorMatching.objects.first()
        initial_score = match.match_score
        
        # Change donor location to be very close
        d1.latitude = 0.01
        d1.save()
        
        generate_matches(self.blood_request)
        match.refresh_from_db()
        
        self.assertNotEqual(match.match_score, initial_score)
        self.assertEqual(match.status, DonorMatching.Status.PENDING)

    def test_accepted_match_not_modified(self):
        # 12. Existing ACCEPTED match keeps ACCEPTED status.
        # 15. Existing responded_at is not overwritten.
        d1 = self._create_donor('d1@e.com', 'O+', lat=0.1, lon=0.0)
        generate_matches(self.blood_request)
        match = DonorMatching.objects.first()
        initial_distance = match.distance_km
        
        match.status = DonorMatching.Status.ACCEPTED
        t = timezone.now()
        match.responded_at = t
        match.save()
        
        # Change donor location
        d1.latitude = 0.01
        d1.save()
        
        generate_matches(self.blood_request)
        match.refresh_from_db()
        
        self.assertEqual(match.status, DonorMatching.Status.ACCEPTED)
        self.assertEqual(match.responded_at, t)
        self.assertEqual(match.distance_km, initial_distance)

    def test_rejected_match_not_modified(self):
        # 13. Existing REJECTED match keeps REJECTED status.
        d1 = self._create_donor('d1@e.com', 'O+', lat=0.1, lon=0.0)
        generate_matches(self.blood_request)
        match = DonorMatching.objects.first()
        match.status = DonorMatching.Status.REJECTED
        match.save()
        
        d1.latitude = 0.01
        d1.save()
        
        generate_matches(self.blood_request)
        match.refresh_from_db()
        self.assertEqual(match.status, DonorMatching.Status.REJECTED)

    def test_cancelled_match_not_modified(self):
        # 14. Existing CANCELLED match keeps CANCELLED status.
        d1 = self._create_donor('d1@e.com', 'O+', lat=0.1, lon=0.0)
        generate_matches(self.blood_request)
        match = DonorMatching.objects.first()
        match.status = DonorMatching.Status.CANCELLED
        match.save()
        
        generate_matches(self.blood_request)
        match.refresh_from_db()
        self.assertEqual(match.status, DonorMatching.Status.CANCELLED)

    def test_ordering(self):
        # 16. Results are ordered by score descending.
        # 17. Equal scores are ordered by distance ascending.
        # 18. NULL distance values appear after known distances within the same score.
        d_A = self._create_donor('A@e.com', 'O+', lat=0.01, lon=0.0) # score 100
        d_B = self._create_donor('B@e.com', 'O+', lat=0.15, lon=0.0) # score 75, distance ~16km
        d_C = self._create_donor('C@e.com', 'O+', lat=0.17, lon=0.0) # score 75, distance ~18km
        d_D = self._create_donor('D@e.com', 'O+') # score 50, distance None
        d_E = self._create_donor('E@e.com', 'O+', lat=1.0, lon=0.0) # score 25
        
        matches = list(generate_matches(self.blood_request))
        self.assertEqual(len(matches), 5)
        self.assertEqual(matches[0].donor, d_A)
        self.assertEqual(matches[1].donor, d_B)
        self.assertEqual(matches[2].donor, d_C)
        self.assertEqual(matches[3].donor, d_D)
        self.assertEqual(matches[4].donor, d_E)

    def test_transaction_rollback_on_error(self):
        # 19. Database transaction is used correctly.
        self._create_donor('d1@e.com', 'O+')
        d2 = self._create_donor('d2@e.com', 'O+')
        
        original_get_or_create = DonorMatching.objects.get_or_create
        
        def side_effect(*args, **kwargs):
            if kwargs.get('donor') == d2:
                raise IntegrityError("Simulated DB error")
            return original_get_or_create(*args, **kwargs)
            
        with patch('matching.orchestrator.DonorMatching.objects.get_or_create', side_effect=side_effect):
            with self.assertRaises(IntegrityError):
                generate_matches(self.blood_request)
                
        self.assertEqual(DonorMatching.objects.count(), 0)

    def test_unrelated_matches_unaffected(self):
        # 20. Existing unrelated matches for other requests are unaffected.
        req2 = BloodRequest.objects.create(
            requester=self.requester_user,
            blood_group=BloodRequest.BloodGroup.A_POS,
            units_required=1,
            hospital_name='H2',
            location='L2',
            required_date=self.today + datetime.timedelta(days=2),
            urgency=BloodRequest.Urgency.NORMAL
        )
        self._create_donor('d1@e.com', 'O+')
        
        generate_matches(req2)
        self.assertEqual(DonorMatching.objects.filter(blood_request=req2).count(), 1)
        
        generate_matches(self.blood_request)
        self.assertEqual(DonorMatching.objects.filter(blood_request=self.blood_request).count(), 1)
        self.assertEqual(DonorMatching.objects.filter(blood_request=req2).count(), 1)
