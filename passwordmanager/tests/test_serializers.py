from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from accounts.serializers import (
    CreateUserSerializer,
    ChangePasswordSerializer,
    CheckIdentifierAvailableSerializer,
)
from accounts.models import UserProfile
from rest_framework.test import APIClient


class CreateUserSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "username": "test@example.com",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
        }

    def test_valid_user_creation(self):
        """Test creating a user with valid data"""
        serializer = CreateUserSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, self.valid_data["username"])
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertTrue(user.check_password(self.valid_data["password"]))

    # def test_password_mismatch(self):
    #     """Test validation fails when passwords don't match"""
    #     data = self.valid_data.copy()
    #     data["confirm_password"] = "DifferentPassword"
    #     serializer = CreateUserSerializer(data=data)
    #     self.assertFalse(serializer.is_valid())
    #     self.assertIn("password", serializer.errors)

    def test_weak_password(self):
        """Test validation fails with weak password"""
        data = self.valid_data.copy()
        data["password"] = data["confirm_password"] = "weak"
        serializer = CreateUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_duplicate_email(self):
        """Test validation fails with duplicate email"""
        User.objects.create_user(
            username="differentUsername",
            email=self.valid_data["email"],
            password=self.valid_data["password"],
        )
        serializer = CreateUserSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    # def test_duplicate_username(self):
    #     """Test validation fails with duplicate username"""
    #     User.objects.create_user(
    #         username=self.valid_data["username"],
    #         email="different@email.com",
    #         password=self.valid_data["password"],
    #     )
    #     serializer = CreateUserSerializer(data=self.valid_data)
    #     self.assertFalse(serializer.is_valid())
    #     self.assertIn("username", serializer.errors)


class ChangePasswordSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="OldPassword123!"
        )
        self.factory = APIRequestFactory()
        self.client = APIClient()

    def test_valid_password_change(self):
        """Test password change with valid data"""
        request = self.factory.post("/test/")
        request.user = self.user

        data = {
            "old_password": "OldPassword123!",
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!",
        }

        serializer = ChangePasswordSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())

    def test_wrong_old_password(self):
        """Test validation fails with wrong old password"""
        request = self.factory.post("/test/")
        request.user = self.user

        data = {
            "old_password": "WrongPassword",
            "new_password": "NewPassword123!",
            # "confirm_new_password": "NewPassword123!",
        }

        serializer = ChangePasswordSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("old_password", serializer.errors)

    # def test_new_password_mismatch(self):
    #     """Test validation fails when new passwords don't match"""
    #     request = self.factory.post("/test/")
    #     request.user = self.user
    #     # self.client.force_authenticate(user=self.user)

    #     data = {
    #         "old_password": "OldPassword123!",
    #         "new_password": "NewPassword123!",
    #         # "confirm_new_password": "DifferentPassword",
    #     }

    #     serializer = ChangePasswordSerializer(data=data, context={"request": request})
    #     self.assertFalse(serializer.is_valid())
    #     self.assertIn("new_password", serializer.errors)


# class SetMFASerializerTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='TestPassword123!'
#         )
#         UserProfile.objects.create(user=self.user)
#         self.factory = APIRequestFactory()

#     def test_enable_mfa_valid(self):
#         """Test enabling MFA with valid password"""
#         request = self.factory.post('/test/')
#         request.user = self.user

#         data = {
#             'mfa_enabled': True,
#             'password': 'TestPassword123!'
#         }

#         serializer = SetMFASerializer(data=data, context={'request': Request(request)})
#         self.assertTrue(serializer.is_valid())

#     def test_disable_mfa_valid(self):
#         """Test disabling MFA with valid password"""
#         request = self.factory.post('/test/')
#         request.user = self.user

#         data = {
#             'mfa_enabled': False,
#             'password': 'TestPassword123!'
#         }

#         serializer = SetMFASerializer(data=data, context={'request': Request(request)})
#         self.assertTrue(serializer.is_valid())

#     def test_wrong_password(self):
#         """Test validation fails with wrong password"""
#         request = self.factory.post('/test/')
#         request.user = self.user

#         data = {
#             'mfa_enabled': True,
#             'password': 'WrongPassword'
#         }

#         serializer = SetMFASerializer(data=data, context={'request': Request(request)})
#         self.assertFalse(serializer.is_valid())
#         self.assertIn('password', serializer.errors)


class CheckIdentifierAvailableSerializerTest(TestCase):
    def test_valid_serializer_creation(self):
        """Test serializer accepts valid data"""
        query = {"q": "testuser"}
        serializer = CheckIdentifierAvailableSerializer(data=query)
        self.assertTrue(serializer.is_valid())
