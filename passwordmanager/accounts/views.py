import io
from django.conf import settings
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

import pyotp
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from .mfa_utils import (
    send_mfa_challenge,
    send_mfa_enrollment_email,
    set_mfa_challenge_in_user_session,
    verify_mfa_challenge,
)

from .totp_mfa_utils import generate_qr_from_uri, save_mfa_totp_enrollment

from .sms_mfa_utils import (
    set_mfa_sms_enroll_challenge_in_user_session,
    save_mfa_sms_enrollment,
    send_mfa_sms_challenge,
)

from .serializers import (
    AuthResponseSerializer,
    ChangePasswordSerializer,
    CheckIdentifierAvailableSerializer,
    CreateUserSerializer,
    CSRFTokenSerializer,
    EnrollEmailMFARequestSerializer,
    EnrollSMSMFARequestSerializer,
    EnrollTOTPMFARequestSerializer,
    SessionLoginSerializer,
    SessionLogoutSerializer,
    SetMFASerializer,
    StartMFAChallengeSerializer,
    UserInfoLookupSerializer,
    VerifyMFAChallengeSerializer,
    VerifyMFASerializer,
    VerifyTOTPMFARequestSerializer,
)
import logging

logger = logging.getLogger(__name__)


class CredentialsLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AuthResponseSerializer

    def post(self, request):
        if not settings.DEBUG:
            return Response(
                {"detail": "This endpoint is only available in debug mode."},
                status=status.HTTP_403_FORBIDDEN,
            )

        username = request.data.get("username")
        if not username:
            username = request.data.get("email")

        if not username:
            return Response(
                {"detail": "Username or email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            csrf_token = get_token(request)
            sessionid = request.session.session_key

            data = {
                "username": user.username,
                "sessionid": sessionid,
                "csrftoken": csrf_token,
            }

            serializer = AuthResponseSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class CreateUserView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CreateUserSerializer

    def post(self, request):
        print("CreateUserView called with data:", request.data)
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(
                    {
                        "email": user.email,
                        "username": user.username,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "detail": f"User {user.username} created.",
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError:
                return Response(
                    {"detail": ["A user with that email already exists."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CSRFTokenView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CSRFTokenSerializer

    def get(self, request):
        # if not settings.DEBUG:
        #     return Response(
        #         {"detail": "This endpoint is only available in debug mode."},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )

        csrf_token = get_token(request)
        return Response({"csrftoken": csrf_token}, status=status.HTTP_200_OK)


class CheckIdentifierAvailableView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CheckIdentifierAvailableSerializer

    def get(self, request):
        identifier = request.query_params.get("q")
        if not identifier:
            return Response(
                {"detail": "query required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # apparently a safe way to check existence without raising exceptions
        filter_kwargs = {"email": identifier}
        exists = User.objects.filter(**filter_kwargs).exists()
        if not exists:
            filter_kwargs = {"username": identifier}
            exists = User.objects.filter(**filter_kwargs).exists()

        return Response(
            {
                "available": not exists,
                "detail": f"{identifier} is {'already taken' if exists else 'available'}.",
            },
            status=status.HTTP_200_OK,
        )


class SessionLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SessionLoginSerializer

    def post(self, request):
        """Django's session framework automatically handles:
        - Secure session ID generation
        - Session expiration
        - Session rotation on authentication state changes
        - HttpOnly cookies (when using cookie sessions)
        - Secure flag for HTTPS
        """
        username = request.data.get("username")
        if not username:
            username = request.data.get("email")

        if not username:
            return Response(
                {"detail": "Username or email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # this does the magic for session auth, i.e. the above list
            login(request, user)
            return Response(
                {"detail": "Login successful"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class SessionLogoutView(APIView):
    """
    Logs the user out by flushing the session.
    This invalidates the session ID and removes all session data.
    The sessionid cookie will be cleared by the browser.
    """

    permission_classes = [AllowAny]
    serializer_class = SessionLogoutSerializer

    def post(self, request):
        """as long as the sessionid cookie is set in the request, this will log the user out"""
        try:
            logout(request)  # calls session.flush()
            return Response(
                {"detail": "Logout successful"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error("An error occurred during logout.", exc_info=True)
            return Response(
                {"detail": "An error occurred during logout."},
            )


class ChangePasswordView(APIView):
    """Allows users to change their password.
    Requires the old password for verification.
    If the old password is correct, the new password is set."""

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"detail": "Password changed successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetUserMFAView(APIView):
    """Allows users to enable or disable MFA.
    Requires the user's password for verification."""

    permission_classes = [IsAuthenticated]
    serializer_class = SetMFASerializer

    def post(self, request):
        serializer = SetMFASerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        mfa_enabled = serializer.validated_data["mfa_enabled"]
        user = request.user
        user.userprofile.mfa_enabled = mfa_enabled
        user.userprofile.save()

        return Response(
            {"detail": f"MFA {'enabled' if mfa_enabled else 'disabled'} successfully."}
        )


class SendEmailMFAEnrollmentRequestView(APIView):
    """Sends an email with a token to verify MFA enrollment via email."""

    permission_classes = [IsAuthenticated]
    serializer_class = EnrollEmailMFARequestSerializer

    def post(self, request):
        serializer = EnrollEmailMFARequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        try:
            send_mfa_enrollment_email(user, token)
        except Exception as e:
            logger.error("Failed to send MFA enrollment email.", exc_info=True)
            return Response(
                {"detail": "Failed to send MFA enrollment email."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = Response(
            {
                "detail": "MFA enrollment email sent.",
                "email": user.email,
            },
            status=200,
        )

        if not settings.DEBUG:
            response["uid"] = uid
            response["token"] = token

        return response


class VerifyEmailMFAEnrollmentView(APIView):
    """Verifies the email link and enables MFA for the user."""

    permission_classes = [AllowAny]
    serializer_class = VerifyMFASerializer

    def get(self, request):
        serializer = VerifyMFASerializer(data=request.query_params)

        if serializer.is_valid():
            user = serializer.user

            user.userprofile.mfa_enabled = True
            user.userprofile.save()

            return Response({"detail": "Email-based MFA enabled."})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StartMFAChallengeView(APIView):
    """Starts the MFA challenge by sending a code to the user."""

    permission_classes = [IsAuthenticated]
    serializer_class = StartMFAChallengeSerializer

    def post(self, request):
        serializer = StartMFAChallengeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = None

        try:
            user = request.user

            if not user.userprofile.mfa_enabled:
                return Response(
                    {"detail": "MFA is not enabled for this user."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            mfa_type = serializer.validated_data["mfa_type"]
            code = set_mfa_challenge_in_user_session(request)
            send_mfa_challenge(user, mfa_type, code)
            response = Response({"detail": "MFA challenge sent."})
        except Exception as e:
            logger.error(f"Failed to send MFA challenge: {e}")
            response = Response(
                {"detail": "Failed to send MFA challenge."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if settings.DEBUG:
            response.data["code"] = code
            response.data["mfa_type"] = mfa_type
            response.data["email"] = user.email

        return response


class VerifyMFAChallengeView(APIView):
    """Verifies the MFA challenge."""

    permission_classes = [IsAuthenticated]
    serializer_class = VerifyMFAChallengeSerializer

    def post(self, request):
        serializer = VerifyMFAChallengeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        try:
            verify_mfa_challenge(request, code)
        except ValueError as e:
            logger.error(f"MFA challenge verification failed: {e}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "MFA challenge verified."})


class SendSMSMFAEnrollmentRequestView(APIView):
    """Enrolls the user for SMS-based MFA.
    sms_number must be in E.164 format (e.g., +1234567890).
    (see https://www.twilio.com/docs/glossary/what-e164)"""

    permission_classes = [IsAuthenticated]
    serializer_class = EnrollSMSMFARequestSerializer

    def post(self, request):
        serializer = EnrollSMSMFARequestSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            code = set_mfa_sms_enroll_challenge_in_user_session(
                request, serializer.validated_data["sms_number"]
            )
            sms_number = serializer.validated_data["sms_number"]
            send_mfa_sms_challenge(request, sms_number)
            response = Response({"detail": "SMS MFA enrollment challenge sent."})
        except Exception as e:
            logger.error(f"Failed to send SMS MFA enrollment challenge: {e}")
            response = Response(
                {"detail": "Failed to send SMS MFA enrollment challenge."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return response


class VerifySMSMFAEnrollmentView(APIView):
    """Verifies the MFA challenge."""

    permission_classes = [IsAuthenticated]
    serializer_class = VerifyMFAChallengeSerializer

    def post(self, request):
        serializer = VerifyMFAChallengeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        try:
            verified = verify_mfa_challenge(request, code)
            if verified:
                save_mfa_sms_enrollment(request)
        except ValueError as e:
            logger.error(f"MFA challenge verification failed: {e}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "MFA challenge verified."})


class StartTOTPMFAEnrollmentView(APIView):
    """Starts the TOTP MFA enrollment by generating a secret key.
    see https://pyauth.github.io/pyotp/#installation"""

    permission_classes = [IsAuthenticated]
    serializer_class = EnrollTOTPMFARequestSerializer

    def get(self, request):
        user = request.user
        secret = pyotp.random_base32()
        request.session["mfa_totp_enrollment_secret"] = secret
        # user.userprofile.totp_secret = secret

        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=user.email, issuer_name="OSUPasswordManager")

        qr = generate_qr_from_uri(uri)

        return Response(
            {
                "uri": uri,
                "secret": secret,
                "qr_code": f"data:image/png;base64,{qr}",
            }
        )


class VerifyTOTPMFAEnrollmentView(APIView):
    """Verifies a TOTP MFA enrollment.
    If user is already enrolled, it will enable TOTP MFA for MFA access.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = VerifyTOTPMFARequestSerializer

    def post(self, request):
        serializer = VerifyTOTPMFARequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        secret = (
            user.userprofile.totp_secret
            if user.userprofile.totp_secret
            else request.session.get("mfa_totp_enrollment_secret", None)
        )
        otp = serializer.validated_data["otp"]

        try:
            totp = pyotp.TOTP(secret)
            if not totp.verify(otp):
                return Response(
                    {"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST
                )

            # If the user is not already enrolled, enable TOTP MFA
            if not user.userprofile.totp_enabled:
                save_mfa_totp_enrollment(request)

            else:
                request.session["mfa_verified"] = True
                request.session.save()

        except Exception as e:
            logger.error(f"Failed to verify TOTP MFA enrollment: {e}")
            response = Response(
                {"detail": "Failed to verify TOTP MFA enrollment."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = Response(
            {
                "detail": "TOTP MFA enrollment successful.",
                "secret": secret,
                "uri": totp.provisioning_uri(
                    name=user.email, issuer_name="OSUPasswordManager"
                ),
            }
        )

        return response


class UserInfoLookupView(APIView):
    """Returns the user's information, including MFA status."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserInfoLookupSerializer

    def get(self, request):
        user = request.user
        data = {
            "username": user.username,
            "email": user.email,
            "mfa_enabled": user.userprofile.mfa_enabled,
            "mfa_sms_enabled": user.userprofile.mfa_sms_enabled,
            "mfa_totp_enabled": user.userprofile.totp_enabled,
        }
        return Response(data, status=status.HTTP_200_OK)
