import jwt
import requests
from django.conf import settings
from rest_framework import authentication, exceptions
from django.core.cache import cache


def validate_oidc_token(token):
    """
    Validate the OIDC token and return user claims.
    """
    try:
        jwks = get_jwks()

        # header constains the key ID which is looked up in the JWKS
        # to find the public key used to sign/validae the token
        unverified_header = jwt.get_unverified_header(token)
        signing_key = get_signing_key(jwks, unverified_header.get("kid"))
        decoded_token = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.OIDC_AUDIENCE,
            issuer=settings.OIDC_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            },
        )

        return decoded_token

    except jwt.exceptions.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed("Token has expired")
    except jwt.exceptions.InvalidTokenError as e:
        raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")


def get_jwks():
    """
    get JWKS (JSON Web Key Set) from the OIDC configuration endpoint (cached).
    """
    cache_key = "jwks_configuration"
    config = cache.get(cache_key)

    if not config:
        config_url = f"{settings.OIDC_ISSUER}/.well-known/jwks.json"
        response = requests.get(config_url, timeout=10)
        response.raise_for_status()
        config = response.json()
        cache.set(cache_key, config, 3600)

    return config


def get_signing_key(jwks, kid):
    """
    Get the signing key from JWKS based on key ID.
    """
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            # jwt expects a PEM key for some reason and I don't feel like
            # figuring out why -- so convert to PEM, based on some internet examples
            # this seems to work...
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import base64

            n = base64.urlsafe_b64decode(key["n"] + "==")
            e = base64.urlsafe_b64decode(key["e"] + "==")
            public_numbers = rsa.RSAPublicNumbers(
                int.from_bytes(e, "big"), int.from_bytes(n, "big")
            )
            public_key = public_numbers.public_key()
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            return pem

    raise exceptions.AuthenticationFailed("Could not get signing key")
