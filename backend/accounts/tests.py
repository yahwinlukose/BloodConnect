from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('auth_login')
        self.logout_url = reverse('auth_logout')
        self.me_url = reverse('auth_me')
        self.refresh_url = reverse('auth_token_refresh')
        
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890',
            'role': User.Role.USER
        }

    def test_successful_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_duplicate_email_registration(self):
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_successful_login(self):
        self.client.post(self.register_url, self.user_data)
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_login(self):
        self.client.post(self.register_url, self.user_data)
        login_data = {
            'email': self.user_data['email'],
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_me_endpoint(self):
        self.client.post(self.register_url, self.user_data)
        login_response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])

    def test_unauthenticated_me_endpoint(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        self.client.post(self.register_url, self.user_data)
        login_response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        refresh_token = login_response.data['refresh']
        
        response = self.client.post(self.refresh_url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_logout(self):
        self.client.post(self.register_url, self.user_data)
        login_response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        logout_response = self.client.post(self.logout_url, {'refresh': refresh_token})
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # Verify the refresh token is blacklisted by trying to use it
        refresh_attempt = self.client.post(self.refresh_url, {'refresh': refresh_token})
        self.assertEqual(refresh_attempt.status_code, status.HTTP_401_UNAUTHORIZED)
