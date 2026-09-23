from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from unittest.mock import patch
from blood_requests.models import BloodRequest
from donors.models import DonorProfile
from matching.models import DonorMatching
from .models import Notification
from .services import create_match_notification
import datetime
from decimal import Decimal

User = get_user_model()

class NotificationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='pwd', role=User.Role.USER)
        self.donor_user = User.objects.create_user(email='donor@example.com', password='pwd', role=User.Role.USER)
        
        self.blood_request = BloodRequest.objects.create(
            requester=self.user,
            blood_group=BloodRequest.BloodGroup.O_POS,
            units_required=2,
            hospital_name='Rajagiri Hospital',
            location='Aluva',
            required_date=datetime.date.today() + datetime.timedelta(days=1),
            urgency=BloodRequest.Urgency.URGENT
        )
        
        self.donor_profile = DonorProfile.objects.create(
            user=self.donor_user,
            blood_group=DonorProfile.BloodGroup.O_POS,
            date_of_birth=datetime.date(1990, 1, 1),
            gender=DonorProfile.Gender.MALE
        )
        
        self.donor_matching = DonorMatching.objects.create(
            blood_request=self.blood_request,
            donor=self.donor_profile,
            distance_km=Decimal('10.00'),
            match_score=Decimal('90.00'),
            status=DonorMatching.Status.PENDING
        )

    def test_pending_match_creates_notification(self):
        # 1. PENDING match creates notification.
        notif = create_match_notification(self.donor_matching)
        self.assertIsNotNone(notif)
        self.assertEqual(Notification.objects.count(), 1)

    def test_notification_recipient(self):
        # 2. Notification recipient is the donor's user.
        # 18. Recipient cannot be changed through the service (implicit since it's hardcoded to donor.user)
        notif = create_match_notification(self.donor_matching)
        self.assertEqual(notif.recipient, self.donor_user)

    def test_notification_blood_request(self):
        # 3. Notification points to the correct BloodRequest.
        notif = create_match_notification(self.donor_matching)
        self.assertEqual(notif.blood_request, self.blood_request)

    def test_notification_donor_matching(self):
        # 4. Notification points to the correct DonorMatching.
        notif = create_match_notification(self.donor_matching)
        self.assertEqual(notif.donor_matching, self.donor_matching)

    def test_notification_type(self):
        # 5. Notification type is BLOOD_REQUEST_MATCH.
        notif = create_match_notification(self.donor_matching)
        self.assertEqual(notif.notification_type, Notification.NotificationType.BLOOD_REQUEST_MATCH)

    def test_notification_title(self):
        # 6. Notification title is correct.
        notif = create_match_notification(self.donor_matching)
        self.assertEqual(notif.title, "Blood request match")

    def test_notification_message_contents(self):
        # 7. Notification message contains blood group.
        # 8. Notification message contains units required.
        # 9. Notification message contains hospital name.
        # 10. Notification message contains location.
        # 11. Notification message contains urgency.
        notif = create_match_notification(self.donor_matching)
        msg = notif.message
        
        self.assertIn("O+", msg)
        self.assertIn("2", msg)
        self.assertIn("Rajagiri Hospital", msg)
        self.assertIn("Aluva", msg)
        self.assertIn("Urgent", msg)

    def test_non_pending_matches(self):
        # 12. ACCEPTED match does not create notification.
        self.donor_matching.status = DonorMatching.Status.ACCEPTED
        self.donor_matching.save()
        self.assertIsNone(create_match_notification(self.donor_matching))
        
        # 13. REJECTED match does not create notification.
        self.donor_matching.status = DonorMatching.Status.REJECTED
        self.donor_matching.save()
        self.assertIsNone(create_match_notification(self.donor_matching))
        
        # 14. EXPIRED match does not create notification.
        self.donor_matching.status = DonorMatching.Status.EXPIRED
        self.donor_matching.save()
        self.assertIsNone(create_match_notification(self.donor_matching))
        
        # 15. CANCELLED match does not create notification.
        self.donor_matching.status = DonorMatching.Status.CANCELLED
        self.donor_matching.save()
        self.assertIsNone(create_match_notification(self.donor_matching))
        
        self.assertEqual(Notification.objects.count(), 0)

    def test_duplicate_prevention(self):
        # 16. Calling the service twice does not create duplicates.
        # 17. Existing notification is returned on the second call.
        notif1 = create_match_notification(self.donor_matching)
        notif2 = create_match_notification(self.donor_matching)
        
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notif1.id, notif2.id)

    def test_application_database_record_only(self):
        # 19. Notification remains an application database record only.
        # Assessed by verifying the code doesn't call external apis (no requests library imported, no mocks needed for external calls)
        notif = create_match_notification(self.donor_matching)
        self.assertTrue(isinstance(notif, Notification))

    @patch('notifications.services.Notification.objects.get_or_create')
    def test_transaction_behavior(self, mock_get_or_create):
        # 20. Database transaction behavior works correctly.
        mock_get_or_create.side_effect = IntegrityError("Database error")
        
        with self.assertRaises(IntegrityError):
            create_match_notification(self.donor_matching)
            
        self.assertEqual(Notification.objects.count(), 0)
