from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mfa_enabled = models.BooleanField(default=False)

    mfa_sms_enabled = models.BooleanField(default=False)
    sms_number = models.CharField(max_length=15, blank=True, null=True)

    totp_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
