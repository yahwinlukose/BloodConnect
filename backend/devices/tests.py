from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from .models import DeviceToken

class DeviceTokenTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='password123', role=User.Role.USER)
        self.other_user = User.objects.create_user(email='other@example.com', password='password123', role=User.Role.USER)
        
        self.url = reverse('device-token-list')
        
    def test_unauthenticated_rejection(self):
        response = self.client.post(self.url, {'token': 'test_token'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_authenticated_registration(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'token': 'test_fcm_token_123',
            'device_type': DeviceToken.DeviceType.ANDROID
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeviceToken.objects.count(), 1)
        
        token_obj = DeviceToken.objects.first()
        self.assertEqual(token_obj.user, self.user)
        self.assertEqual(token_obj.token, 'test_fcm_token_123')
        self.assertEqual(token_obj.device_type, 'ANDROID')
        self.assertTrue(token_obj.is_active)
        
    def test_duplicate_token_registration(self):
        self.client.force_authenticate(user=self.user)
        data = {'token': 'duplicate_token'}
        
        # First registration
        response1 = self.client.post(self.url, data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeviceToken.objects.count(), 1)
        
        # Second registration of same token by same user
        response2 = self.client.post(self.url, data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK) # Should return 200 OK
        self.assertEqual(DeviceToken.objects.count(), 1) # Still 1 token in DB
        
    def test_reassignment_to_new_user(self):
        # User 1 registers token
        DeviceToken.objects.create(user=self.user, token='shared_token')
        
        # User 2 logs in on same device and registers same token
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(self.url, {'token': 'shared_token'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DeviceToken.objects.count(), 1)
        
        token_obj = DeviceToken.objects.get(token='shared_token')
        self.assertEqual(token_obj.user, self.other_user) # Token should now belong to other_user
        
    def test_reactivation_of_inactive_token(self):
        self.client.force_authenticate(user=self.user)
        token_obj = DeviceToken.objects.create(user=self.user, token='inactive_token', is_active=False)
        
        response = self.client.post(self.url, {'token': 'inactive_token'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        token_obj.refresh_from_db()
        self.assertTrue(token_obj.is_active)
        
    def test_multiple_tokens_for_one_user(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url, {'token': 'token_1'})
        self.client.post(self.url, {'token': 'token_2', 'device_type': 'IOS'})
        
        self.assertEqual(DeviceToken.objects.filter(user=self.user).count(), 2)
        
    def test_listing_only_current_users_active_tokens(self):
        # User's active token
        DeviceToken.objects.create(user=self.user, token='active_token_1', is_active=True)
        # User's inactive token
        DeviceToken.objects.create(user=self.user, token='inactive_token_1', is_active=False)
        # Other user's active token
        DeviceToken.objects.create(user=self.other_user, token='other_token', is_active=True)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['token'], 'active_token_1')
        
    def test_deleting_deactivating_own_token(self):
        self.client.force_authenticate(user=self.user)
        token_obj = DeviceToken.objects.create(user=self.user, token='delete_me', is_active=True)
        
        detail_url = reverse('device-token-detail', args=[token_obj.id])
        response = self.client.delete(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        token_obj.refresh_from_db()
        self.assertFalse(token_obj.is_active) # Should be deactivated, not deleted
        
    def test_prevent_access_to_another_users_token(self):
        self.client.force_authenticate(user=self.user)
        other_token = DeviceToken.objects.create(user=self.other_user, token='other_token', is_active=True)
        
        detail_url = reverse('device-token-detail', args=[other_token.id])
        
        # Try to GET
        response_get = self.client.get(detail_url)
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND)
        
        # Try to DELETE
        response_delete = self.client.delete(detail_url)
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_invalid_device_type(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'token': 'test_fcm_token_123',
            'device_type': 'INVALID_TYPE'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('device_type', response.data)
        
    def test_blank_token(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'token': '   '})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
        
    def test_user_cannot_be_supplied_by_client(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'token': 'my_token',
            'user': self.other_user.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        token_obj = DeviceToken.objects.get(token='my_token')
        self.assertEqual(token_obj.user, self.user) # Should be self.user, ignoring the client provided user
