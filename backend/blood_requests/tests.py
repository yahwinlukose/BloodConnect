from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import BloodRequest
import datetime

User = get_user_model()

class BloodRequestModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='requester@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            role=User.Role.USER
        )
        
        self.valid_data = {
            'requester': self.user,
            'blood_group': BloodRequest.BloodGroup.O_POS,
            'units_required': 2,
            'hospital_name': 'City Hospital',
            'location': 'New York',
            'required_date': datetime.date.today() + datetime.timedelta(days=2)
        }

    def test_valid_blood_request_creation(self):
        request = BloodRequest.objects.create(**self.valid_data)
        self.assertEqual(BloodRequest.objects.count(), 1)
        self.assertEqual(request.hospital_name, 'City Hospital')
        
    def test_requester_relationship(self):
        request = BloodRequest.objects.create(**self.valid_data)
        self.assertEqual(request.requester, self.user)
        self.assertIn(request, self.user.blood_requests.all())
        
    def test_default_status_is_pending(self):
        request = BloodRequest.objects.create(**self.valid_data)
        self.assertEqual(request.status, BloodRequest.Status.PENDING)
        
    def test_default_urgency_is_normal(self):
        request = BloodRequest.objects.create(**self.valid_data)
        self.assertEqual(request.urgency, BloodRequest.Urgency.NORMAL)
        
    def test_units_required_cannot_be_zero(self):
        invalid_data = self.valid_data.copy()
        invalid_data['units_required'] = 0
        request = BloodRequest(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            request.full_clean()
        self.assertIn('units_required', context.exception.message_dict)

    def test_invalid_latitude_rejected(self):
        invalid_data = self.valid_data.copy()
        invalid_data['latitude'] = 91.0
        request = BloodRequest(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            request.full_clean()
        self.assertIn('latitude', context.exception.message_dict)
        
    def test_invalid_longitude_rejected(self):
        invalid_data = self.valid_data.copy()
        invalid_data['longitude'] = -181.0
        request = BloodRequest(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            request.full_clean()
        self.assertIn('longitude', context.exception.message_dict)
        
    def test_past_required_date_rejected(self):
        invalid_data = self.valid_data.copy()
        invalid_data['required_date'] = datetime.date.today() - datetime.timedelta(days=1)
        request = BloodRequest(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            request.full_clean()
        self.assertIn('required_date', context.exception.message_dict)

    def test_all_valid_blood_groups_accepted(self):
        for bg_code, _ in BloodRequest.BloodGroup.choices:
            data = self.valid_data.copy()
            data['blood_group'] = bg_code
            request = BloodRequest(**data)
            try:
                request.full_clean()
            except ValidationError:
                self.fail(f"Validation failed for valid blood group {bg_code}")

    def test_all_urgency_choices_accepted(self):
        for urgency_code, _ in BloodRequest.Urgency.choices:
            data = self.valid_data.copy()
            data['urgency'] = urgency_code
            request = BloodRequest(**data)
            try:
                request.full_clean()
            except ValidationError:
                self.fail(f"Validation failed for valid urgency {urgency_code}")

    def test_all_status_choices_accepted(self):
        for status_code, _ in BloodRequest.Status.choices:
            data = self.valid_data.copy()
            data['status'] = status_code
            request = BloodRequest(**data)
            try:
                request.full_clean()
            except ValidationError:
                self.fail(f"Validation failed for valid status {status_code}")

    def test_str_method(self):
        request = BloodRequest.objects.create(**self.valid_data)
        # We don't know the exact ID before creation, so we check after
        expected_str = f"Blood Request #{request.id} - {BloodRequest.BloodGroup.O_POS} - {BloodRequest.Status.PENDING}"
        self.assertEqual(str(request), expected_str)
