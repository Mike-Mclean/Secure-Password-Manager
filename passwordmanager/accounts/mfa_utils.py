from datetime import datetime, timedelta

import logging
import random
import string

from django.conf import settings
from django.urls import reverse


MFA_EXPIRATION_MINUTES = 120  # MFA validation is good for 2 hours
logger = logging.getLogger(__name__)


def send_mfa_enrollment_email(user, token):
    """
    Sends a MFA enrollment email to the user.
    """
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from django.core.mail import EmailMultiAlternatives

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    subject = "OSUPasswordManager Confirm MFA Enrollment"
    verification_link = f"{settings.FRONTEND_URL}{reverse("accounts:verify_email_mfa")}?uid={uid}&token={token}"
    message = f"Please follow the link below to verify your email and enroll it in Multi Factor Authentication"

    text_content = (
        "Hello,\n\n"
        f"{message}:\n\n"
        f"{verification_link}\n\n"
        "If you did not request this, please ignore this email.\n\n"
        "Thank you,\n"
        "OSUPasswordManager Team"
    )

    html_content = f"""
            <html>
            <body>
                <p>Hello,</p>
                <p>
                {message}:<br />
                <a href="{verification_link}">{verification_link}</a>
                </p>
                <p>
                If you did not request this, please ignore this email.
                </p>
                <p>
                Thank you,<br />
                <strong>OSUPasswordManager Team</strong>
                </p>
            </body>
            </html>
            """

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [user.email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


def set_mfa_challenge_in_user_session(request):
    """
    Sets the MFA challenge in the user's session.
    """

    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    expiration_time = 300  # 5 minutes in seconds
    expiration = datetime.now() + timedelta(seconds=expiration_time)
    expiration = expiration.isoformat()

    request.session["mfa_challenge_code"] = code
    request.session["mfa_challenge_expiration"] = expiration
    request.session.save()

    return code


def send_mfa_challenge(user, mfa_type, code):
    """
    Sends the MFA challenge to the user based on the mfa_type.
    """
    if mfa_type == "email":
        from django.core.mail import send_mail

        subject = "OSUPasswordManager MFA Challenge"
        message = f"Your MFA challenge code is: {code}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    elif mfa_type == "sms":
        logger.warning("SMS MFA is not implemented yet.")
        pass
    else:
        raise ValueError("Invalid MFA type")


def verify_mfa_challenge(request, code):
    """
    Verifies the MFA challenge code.
    """
    if "mfa_challenge_code" not in request.session:
        raise ValueError("No MFA challenge set in session.")

    stored_code = request.session["mfa_challenge_code"]
    expiration = request.session.get("mfa_challenge_expiration", datetime.now())
    expiration = datetime.fromisoformat(expiration)

    if datetime.now() > expiration:
        raise ValueError("MFA challenge has expired.")

    if stored_code != code:
        raise ValueError("Invalid MFA challenge code.")

    mfa_verified_expiration = datetime.now() + timedelta(minutes=MFA_EXPIRATION_MINUTES)
    mfa_verified_expiration = mfa_verified_expiration.isoformat()

    del request.session["mfa_challenge_code"]
    del request.session["mfa_challenge_expiration"]
    request.session["mfa_verified"] = True
    request.session["mfa_verified_expiration"] = mfa_verified_expiration
    request.session.save()

    return True
