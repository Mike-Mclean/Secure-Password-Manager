import base64
import io
import qrcode


def generate_qr_from_uri(uri):
    """
    Generates a QR code from the given URI.
    Returns a base64 encoded string of the QR code image.
    based on tutorial https://medium.com/@rahulmallah785671/create-qr-code-by-using-python-2370d7bd9b8d
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, "PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    return qr_code_base64


def save_mfa_totp_enrollment(request):
    """
    Saves the MFA TOTP enrollment details to the user's profile.
    """
    user = request.user
    user.userprofile.mfa_enabled = True
    user.userprofile.totp_enabled = True
    user.userprofile.totp_secret = request.session.get("mfa_totp_enrollment_secret", "")
    user.userprofile.save()

    del request.session["mfa_challenge_code"]
    del request.session["mfa_challenge_expiration"]
    del request.session["mfa_totp_enrollment_secret"]
    request.session["mfa_verified"] = True
    request.session.save()
