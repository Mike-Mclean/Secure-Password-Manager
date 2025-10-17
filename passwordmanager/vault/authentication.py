from django.contrib.auth.models import User
from rest_framework import authentication, exceptions
from . import auth_helpers
import logging

logger = logging.getLogger(__name__)


class OIDCTokenAuthentication(authentication.BaseAuthentication):
    """
    Simple OIDC authentication that creates VaultUser
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            # For now, let's do simple token validation without full OIDC verification
            # In production, you'd want proper JWT validation
            access_token_payload = auth_helpers.validate_oidc_token(token)

            # Get or create user based on token claims
            # we are only going to use the auht0 account ID as an identifier.
            # the other identifying info can come form the ID token on the front end and
            # will not be persisted in the user DB.
            # if we need it somewhere we can use the access token for a userinfo lookup to auth0
            # alternately, we could add more claims to the access token but this is easier
            vault_user = self.get_or_create_vault_user(access_token_payload)

            # Return the Django User (for DRF compatibility) but store VaultUser in request
            request.vault_user = vault_user
            request.user = vault_user.user
            return (vault_user.user, token)

        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            raise exceptions.AuthenticationFailed("Invalid token")

    def get_or_create_vault_user(self, user_info):
        """
        Get or create a VaultUser based on auth provider information.
        """
        from .models import VaultUser

        auth_provider_id = user_info.get("sub")
        email = user_info.get("email", "")

        try:
            vault_user = VaultUser.objects.select_related("user").get(
                auth_provider_id=auth_provider_id
            )

            vault_user.update_last_accessed()

            logger.info(f"Found existing VaultUser: {auth_provider_id}")

        except VaultUser.DoesNotExist:
            # Create new VaultUser if not exist
            vault_user = VaultUser.create_from_auth_provider(
                auth_provider_id=auth_provider_id, email=email
            )

            logger.info(f"Created new VaultUser: {auth_provider_id}")

        return vault_user
