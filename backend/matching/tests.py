from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from donors.models import DonorProfile
from blood_requests.models import BloodRequest
from .models import DonorMatching
import datetime

User = get_user_model()

class DonorMatchingModelTests(TestCase):
    def setUp(self):
        # Create a requester user and a blood request
        self.requester_user = User.objects.create_user(
            email='requester@example.com',
            password='password123',
            role=User.Role.USER
        )
        self.blood_request = BloodRequest.objects.create(
            requester=self.requester_user,
            blood_group=BloodRequest.BloodGroup.O_POS,
            units_required=1,
            hospital_name='City Hospital',
            location='Downtown',
            required_date=datetime.date.today() + datetime.timedelta(days=2)
        )

        # Create a donor user and profile
        self.donor_user = User.objects.create_user(
            email='donor@example.com',
            password='password123',
            role=User.Role.USER
        )
        self.donor_profile = DonorProfile.objects.create(
            user=self.donor_user,
            blood_group=DonorProfile.BloodGroup.O_POS,
            date_of_birth=datetime.date(1990, 1, 1),
            gender=DonorProfile.Gender.MALE
        )

        self.valid_data = {
            'blood_request': self.blood_request,
            'donor': self.donor_profile,
            'distance_km': 15.5,
            'match_score': 85.0
        }

    def test_valid_donor_matching_creation(self):
        match = DonorMatching.objects.create(**self.valid_data)
        self.assertEqual(DonorMatching.objects.count(), 1)
        self.assertEqual(match.distance_km, 15.5)

    def test_correct_blood_request_relationship(self):
        match = DonorMatching.objects.create(**self.valid_data)
        self.assertEqual(match.blood_request, self.blood_request)
        self.assertIn(match, self.blood_request.matches.all())

    def test_correct_donor_profile_relationship(self):
        match = DonorMatching.objects.create(**self.valid_data)
        self.assertEqual(match.donor, self.donor_profile)
        self.assertIn(match, self.donor_profile.matches.all())

    def test_default_status_is_pending(self):
        match = DonorMatching.objects.create(**self.valid_data)
        self.assertEqual(match.status, DonorMatching.Status.PENDING)

    def test_unique_donor_request_combination_enforced(self):
        DonorMatching.objects.create(**self.valid_data)
        
        # Creating a second match for the same request and donor should raise ValidationError due to full_clean
        with self.assertRaises(ValidationError):
            DonorMatching.objects.create(**self.valid_data)

    def test_negative_distance_rejected(self):
        invalid_data = self.valid_data.copy()
        invalid_data['distance_km'] = -5.0
        match = DonorMatching(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            match.full_clean()
        self.assertIn('distance_km', context.exception.message_dict)

    def test_negative_match_score_rejected(self):
        invalid_data = self.valid_data.copy()
        invalid_data['match_score'] = -10.0
        match = DonorMatching(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            match.full_clean()
        self.assertIn('match_score', context.exception.message_dict)

    def test_match_score_above_100_rejected(self):
        invalid_data = self.valid_data.copy()
        invalid_data['match_score'] = 105.0
        match = DonorMatching(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            match.full_clean()
        self.assertIn('match_score', context.exception.message_dict)

    def test_all_status_choices_accepted(self):
        for status_code, _ in DonorMatching.Status.choices:
            data = self.valid_data.copy()
            data['status'] = status_code
            match = DonorMatching(**data)
            try:
                match.full_clean()
            except ValidationError:
                self.fail(f"Validation failed for valid status {status_code}")

    def test_responded_at_can_be_null(self):
        match = DonorMatching.objects.create(**self.valid_data)
        self.assertIsNone(match.responded_at)
        
        # Test full clean passes with null responded_at
        try:
            match.full_clean()
        except ValidationError:
            self.fail("Validation failed when responded_at is null")

    def test_str_method(self):
        match = DonorMatching.objects.create(**self.valid_data)
        expected_str = f"Match #{match.id} - Request #{self.blood_request.id} - {self.donor_profile} - {DonorMatching.Status.PENDING}"
        self.assertEqual(str(match), expected_str)
