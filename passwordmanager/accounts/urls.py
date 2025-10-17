from django.urls import path
from django.conf import settings
from accounts.views import (
    ChangePasswordView,
    CheckIdentifierAvailableView,
    CredentialsLoginView,
    CreateUserView,
    CSRFTokenView,
    SendEmailMFAEnrollmentRequestView,
    SessionLoginView,
    SessionLogoutView,
    # SetUserMFAView,
    StartMFAChallengeView,
    StartTOTPMFAEnrollmentView,
    UserInfoLookupView,
    VerifyEmailMFAEnrollmentView,
    VerifyMFAChallengeView,
    # VerifySMSMFAEnrollmentView,
    # SendSMSMFAEnrollmentRequestView,
    VerifyTOTPMFAEnrollmentView,
)

# from rest_framework import routers
app_name = "accounts"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create_user"),
    path(
        "check-user/",
        CheckIdentifierAvailableView.as_view(),
        name="check_identifier_available",
    ),
    path(
        "credentials-login/", CredentialsLoginView.as_view(), name="credentials_login"
    ),
    path("login/", SessionLoginView.as_view(), name="session_login"),
    path("logout/", SessionLogoutView.as_view(), name="session_logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("csrf/", CSRFTokenView.as_view(), name="csrf_token"),
    path("userinfo/", UserInfoLookupView.as_view(), name="user_info_lookup"),
    path(
        "mfa/email/enroll/",
        SendEmailMFAEnrollmentRequestView.as_view(),
        name="send_email_mfa",
    ),
    path(
        "mfa/email/verify/",
        VerifyEmailMFAEnrollmentView.as_view(),
        name="verify_email_mfa",
    ),
    path(
        "mfa/totp/enroll/",
        StartTOTPMFAEnrollmentView.as_view(),
        name="enroll_totp_mfa",
    ),
    path(
        "mfa/totp/verify/", VerifyTOTPMFAEnrollmentView.as_view(), name="verify_sms_mfa"
    ),
    # path(
    #     "mfa/sms/enroll/",
    #     SendSMSMFAEnrollmentRequestView.as_view(),
    #     name="send_sms_mfa",
    # ),
    # path(
    #     "mfa/sms/verify/", VerifySMSMFAEnrollmentView.as_view(), name="verify_sms_mfa"
    # ),
    path("mfa/challenge/", StartMFAChallengeView.as_view(), name="send_mfa_challenge"),
    path("mfa/verify/", VerifyMFAChallengeView.as_view(), name="verify_mfa"),
    # path("set-mfa/", SetUserMFAView.as_view(), name="set-mfa"),
]
