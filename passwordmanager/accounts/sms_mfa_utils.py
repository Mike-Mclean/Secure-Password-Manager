from twilio.rest import Client
from django.conf import settings

from .mfa_utils import set_mfa_challenge_in_user_session


def set_mfa_sms_enroll_challenge_in_user_session(request, sms_number):
    """adds the sms number to the session and sets the mfa challenge code"""
    code = set_mfa_challenge_in_user_session(request)
    request.session["mfa_challenge_sms_number"] = sms_number
    request.session.save()

    return code


def save_mfa_sms_enrollment(request):
    """
    Saves the MFA SMS enrollment details to the user's profile.
    """
    user = request.user
    user.userprofile.mfa_sms_enabled = True
    user.userprofile.sms_number = request.session.get("mfa_challenge_sms_number", "")
    user.userprofile.save()

    del request.session["mfa_challenge_sms_number"]
    del request.session["mfa_challenge_code"]
    del request.session["mfa_challenge_expiration"]
    request.session.save()


def send_mfa_sms_challenge(request, sms_number):

    code = request.session["mfa_challenge_code"]
    account_sid = settings.SMS_ACCOUNT_SID
    auth_token = settings.SMS_AUTH_TOKEN
    from_number = settings.SMS_FROM_NUMBER
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=str(sms_number),
        from_=from_number,
        body=f"Your OSUPasswordManager MFA challenge code is: {code}",
    )

    print(message.sid)
