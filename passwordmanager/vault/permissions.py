from rest_framework.permissions import BasePermission


class MFARequiredIfOptedIn(BasePermission):
    message = "MFA verification required before accessing this resource."

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and getattr(user, "userprofile", None):
            if user.userprofile.mfa_enabled:
                return request.session.get("mfa_verified", False)
        return True
