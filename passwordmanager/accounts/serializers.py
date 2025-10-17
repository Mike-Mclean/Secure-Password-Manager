from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator


class AuthResponseSerializer(serializers.Serializer):
    username = serializers.CharField()
    sessionid = serializers.CharField()
    csrftoken = serializers.CharField()


class SessionLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password cannot be empty.")
        return value


class SessionLogoutSerializer(serializers.Serializer):
    sessionid = serializers.CharField(required=False)  # Optional

    # Response fields (if you want to document the response structure)
    detail = serializers.CharField(read_only=True)
    success = serializers.BooleanField(read_only=True)


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    # TODO: frontend does not have password confirm field yet, so this is commented out
    # confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]  # , "confirm_password"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    # def validate_username(self, value):
    #     if User.objects.filter(username=value).exists():
    #         raise serializers.ValidationError(
    #             "A user with this username already exists."
    #         )
    #     return value

    def validate_password(self, value):
        # TODO: Uncomment when frontend has confirm password field
        # if value != self.initial_data.get("confirm_password"):
        #     raise serializers.ValidationError("Passwords do not match.")
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        # Use email as username
        user = User.objects.create_user(username=email, email=email, password=password)
        return user


class GetUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    # confirm_new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        # if value != self.initial_data.get("confirm_new_password"):
        #     raise serializers.ValidationError("New passwords do not match.")
        validate_password(value, self.context["request"].user)
        return value


class CheckIdentifierAvailableSerializer(serializers.Serializer):
    q = serializers.CharField(required=True, max_length=150)

    def validate_q(self, value):
        if not value:
            raise serializers.ValidationError("Identifier cannot be empty.")
        return value


class CSRFTokenSerializer(serializers.Serializer):
    csrftoken = serializers.CharField()


class EnrollEmailMFARequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class SetMFASerializer(serializers.Serializer):
    mfa_enabled = serializers.BooleanField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password.")
        return value


class VerifyMFASerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def validate(self, attrs):
        uidb64 = attrs["uid"]
        token = attrs["token"]

        try:
            user_id = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=user_id)
        except (ValueError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid UID."})

        try:
            token_valid = default_token_generator.check_token(user, token)
            if not token_valid:
                raise serializers.ValidationError(
                    {"token": "Invalid or expired token."}
                )
        except Exception as e:
            raise serializers.ValidationError({"token": str(e)})

        self.user = user
        return attrs


class StartMFAChallengeSerializer(serializers.Serializer):
    mfa_type = serializers.ChoiceField(choices=["email", "sms"], required=True)


class VerifyMFAChallengeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)


class EnrollSMSMFARequestSerializer(serializers.Serializer):
    sms_number = serializers.CharField(required=True, max_length=15)

    def validate_sms_number(self, value):
        if not value.startswith("+"):
            raise serializers.ValidationError("SMS number must be in E.164 format.")
        if not value[1:].isdigit():
            raise serializers.ValidationError(
                "SMS number must start with '+' and contain only digits."
            )
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError(
                "SMS number must be between 10 and 15 characters."
            )
        return value


class EnrollTOTPMFARequestSerializer(serializers.Serializer):
    secret = serializers.CharField(required=True, max_length=16)


class VerifyTOTPMFARequestSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True, max_length=6)


class UserInfoLookupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "mfa_enabled",
            "mfa_sms_enabled",
            "mfa_totp_enabled",
        ]
