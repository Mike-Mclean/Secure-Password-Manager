from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
# from accounts.models import UserProfile


@override_settings(DEBUG=True)
class CredentialsLoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='TestPassword123!'
        )
        self.url = reverse('accounts:credentials_login')  

    def test_login_with_username(self):
        """Test login with username"""
        data = {'username': 'test@example.com', 'password': 'TestPassword123!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sessionid', response.data)
        self.assertIn('csrftoken', response.data)

    def test_login_with_email(self):
        """Test login with email"""
        data = {'email': 'test@example.com', 'password': 'TestPassword123!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    @override_settings(DEBUG=False)
    def test_credentials_login_disabled_in_production(self):
        """Test that credentials login is disabled when DEBUG=False"""
        data = {'username': 'test@example.com', 'password': 'TestPassword123!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'This endpoint is only available in debug mode.')

    @override_settings(DEBUG=True)
    def test_credentials_login_works_in_debug(self):
        """Test that credentials login works when DEBUG=True"""
        data = {'username': 'test@example.com', 'password': 'TestPassword123!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(DEBUG=True)
    def test_missing_username(self):
        """Test login without username or email"""
        data = {'password': 'TestPassword123!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CreateUserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:create_user')  

    def test_create_user_success(self):
        """Test successful user creation"""
        data = {
            'email': 'new@example.com',
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'new@example.com')
        
        # Verify user was created
        user = User.objects.get(email='new@example.com')
        self.assertTrue(user.check_password('NewPassword123!'))

    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email"""
        User.objects.create_user(username='test@example.com', email='test@example.com', password='pass')
        
        data = {
            'email': 'test@example.com',
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_data(self):
        """Test user creation with invalid data"""
        data = {
            'email': 'invalid-email',
            'password': 'weak',
            'confirm_password': 'different'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CSRFTokenViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:csrf_token')  

    def test_get_csrf_token(self):
        """Test getting CSRF token"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrftoken', response.data)


class CheckIdentifierAvailableViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='TestPassword123!'
        )
        self.url = reverse('accounts:check_identifier_available')  

    def test_check_taken_email(self):
        """Test checking taken email"""
        response = self.client.get(self.url, {'q': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['available'])

    def test_missing_query_parameter(self):
        """Test without query parameter"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SessionLoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='TestPassword123!'
        )
        self.url = reverse('accounts:session_login')  

    def test_session_login_success(self):
        """Test successful session login"""
        data = {'username': 'test@example.com', 'password': 'TestPassword123!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Login successful')

    def test_session_login_invalid(self):
        """Test session login with invalid credentials"""
        data = {'username': 'test@example.com', 'password': 'WrongPassword'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SessionLogoutViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='TestPassword123!'
        )
        self.url = reverse('accounts:session_logout')  

    def test_logout_success(self):
        """Test successful logout"""
        # Login first
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ChangePasswordViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='OldPassword123!'
        )
        self.url = reverse('accounts:change_password')  

    def test_change_password_success(self):
        """Test successful password change"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_new_password': 'NewPassword123!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewPassword123!',
            'confirm_new_password': 'NewPassword123!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        """Test password change without authentication"""
        data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_new_password': 'NewPassword123!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# class SetUserMFAViewTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='TestPassword123!'
#         )
#         UserProfile.objects.create(user=self.user)
#         self.url = reverse('accounts:set-mfa')  

#     def test_enable_mfa_success(self):
#         """Test successfully enabling MFA"""
#         self.client.force_authenticate(user=self.user)
        
#         data = {
#             'mfa_enabled': True,
#             'password': 'TestPassword123!'
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('enabled', response.data['detail'])
        
#         # Verify MFA was enabled
#         self.user.userprofile.refresh_from_db()
#         self.assertTrue(self.user.userprofile.mfa_enabled)

#     def test_disable_mfa_success(self):
#         """Test successfully disabling MFA"""
#         self.client.force_authenticate(user=self.user)
#         self.user.userprofile.mfa_enabled = True
#         self.user.userprofile.save()
        
#         data = {
#             'mfa_enabled': False,
#             'password': 'TestPassword123!'
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('disabled', response.data['detail'])

#     def test_mfa_wrong_password(self):
#         """Test MFA change with wrong password"""
#         self.client.force_authenticate(user=self.user)
        
#         data = {
#             'mfa_enabled': True,
#             'password': 'WrongPassword'
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# class SendMFAEnrollmentVerificationViewTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='TestPassword123!'
#         )
#         self.url = reverse('accounts:send-mfa-verification')  

#     def test_send_mfa_verification(self):
#         """Test sending MFA verification email"""
#         self.client.force_authenticate(user=self.user)
        
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['detail'], 'MFA enrollment verification sent.')

#     def test_send_mfa_verification_unauthenticated(self):
#         """Test sending MFA verification without authentication"""
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)