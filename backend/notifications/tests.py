from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from blood_requests.models import BloodRequest
from donors.models import DonorProfile
from matching.models import DonorMatching
from .models import Notification
import datetime

User = get_user_model()

class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='pwd', role=User.Role.USER)
        self.donor_user = User.objects.create_user(email='donor@example.com', password='pwd', role=User.Role.USER)
        
        self.blood_request = BloodRequest.objects.create(
            requester=self.user,
            blood_group=BloodRequest.BloodGroup.O_POS,
            units_required=1,
            hospital_name='H',
            location='L',
            required_date=datetime.date.today() + datetime.timedelta(days=1),
            urgency=BloodRequest.Urgency.NORMAL
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
            distance_km=10.0,
            match_score=90
        )

    def test_notification_can_be_created(self):
        # 1. Notification can be created.
        notif = Notification.objects.create(
            recipient=self.user,
            title='Test',
            message='Test message'
        )
        self.assertEqual(Notification.objects.count(), 1)
        
    def test_recipient_relationship(self):
        # 2. Recipient relationship works.
        notif = Notification.objects.create(
            recipient=self.user,
            title='Test',
            message='Test message'
        )
        self.assertEqual(notif.recipient, self.user)
        self.assertIn(notif, self.user.notifications.all())

    def test_blood_request_relationship(self):
        # 3. BloodRequest relationship works.
        notif = Notification.objects.create(
            recipient=self.user,
            blood_request=self.blood_request,
            title='Test',
            message='Test message'
        )
        self.assertEqual(notif.blood_request, self.blood_request)
        self.assertIn(notif, self.blood_request.notifications.all())

    def test_donor_matching_relationship(self):
        # 4. DonorMatching relationship works.
        notif = Notification.objects.create(
            recipient=self.user,
            donor_matching=self.donor_matching,
            title='Test',
            message='Test message'
        )
        self.assertEqual(notif.donor_matching, self.donor_matching)
        self.assertIn(notif, self.donor_matching.notifications.all())

    def test_defaults(self):
        # 5. Default notification type is BLOOD_REQUEST_MATCH.
        # 6. Default is_read is False.
        # 7. read_at can be NULL.
        notif = Notification.objects.create(
            recipient=self.user,
            title='Test',
            message='Test message'
        )
        self.assertEqual(notif.notification_type, Notification.NotificationType.BLOOD_REQUEST_MATCH)
        self.assertFalse(notif.is_read)
        self.assertIsNone(notif.read_at)

    def test_read_notification_can_have_read_at(self):
        # 8. Read notification can have read_at.
        notif = Notification.objects.create(
            recipient=self.user,
            title='Test',
            message='Test message',
            is_read=True,
            read_at=timezone.now()
        )
        self.assertTrue(notif.is_read)
        self.assertIsNotNone(notif.read_at)

    def test_notification_type_choices(self):
        # 9. Notification type choices are valid.
        for choice, _ in Notification.NotificationType.choices:
            notif = Notification(
                recipient=self.user,
                title='Test',
                message='Test message',
                notification_type=choice
            )
            notif.full_clean()  # Should not raise validation error

    def test_system_notification_without_request(self):
        # 10. SYSTEM notification can exist without BloodRequest.
        notif = Notification.objects.create(
            recipient=self.user,
            title='System Alert',
            message='System going down',
            notification_type=Notification.NotificationType.SYSTEM
        )
        self.assertIsNone(notif.blood_request)
        self.assertIsNone(notif.donor_matching)

    def test_str_representation(self):
        # 11. __str__ works.
        notif = Notification.objects.create(
            recipient=self.user,
            title='Test',
            message='Test message',
            notification_type=Notification.NotificationType.BLOOD_REQUEST_MATCH
        )
        expected = f"Notification #{notif.id} - {self.user.email} - BLOOD_REQUEST_MATCH"
        self.assertEqual(str(notif), expected)

    def test_multiple_notifications_one_user(self):
        # 12. Multiple notifications can belong to one user.
        Notification.objects.create(recipient=self.user, title='T1', message='M1')
        Notification.objects.create(recipient=self.user, title='T2', message='M2')
        self.assertEqual(self.user.notifications.count(), 2)

    def test_retrieved_newest_first(self):
        # 13. Notifications can be retrieved newest first using the intended queryset pattern.
        n1 = Notification.objects.create(recipient=self.user, title='T1', message='M1')
        # Ensure distinct created_at
        n1.created_at = timezone.now() - datetime.timedelta(minutes=10)
        n1.save()
        
        n2 = Notification.objects.create(recipient=self.user, title='T2', message='M2')
        n2.created_at = timezone.now()
        n2.save()
        
        notifications = Notification.objects.filter(recipient=self.user)
        # Using default ordering which should be -created_at
        self.assertEqual(notifications[0], n2)
        self.assertEqual(notifications[1], n1)

    def test_invalid_title(self):
        # 14. Invalid/empty title is rejected.
        notif = Notification(recipient=self.user, title='', message='Test')
        with self.assertRaises(ValidationError) as ctx:
            notif.full_clean()
        self.assertIn('title', ctx.exception.message_dict)

    def test_invalid_message(self):
        # 15. Invalid/empty message is rejected.
        notif = Notification(recipient=self.user, title='Test', message='')
        with self.assertRaises(ValidationError) as ctx:
            notif.full_clean()
        self.assertIn('message', ctx.exception.message_dict)

    def test_unread_with_read_at_rejected(self):
        # 16. A notification marked unread with read_at should fail validation
        notif = Notification(
            recipient=self.user,
            title='Test',
            message='Test',
            is_read=False,
            read_at=timezone.now()
        )
        with self.assertRaises(ValidationError) as ctx:
            notif.full_clean()
        self.assertIn('read_at', ctx.exception.message_dict)

    def test_read_without_read_at_allowed(self):
        # 17. A read notification without read_at should be allowed
        notif = Notification(
            recipient=self.user,
            title='Test',
            message='Test',
            is_read=True,
            read_at=None
        )
        try:
            notif.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly for read without read_at")
