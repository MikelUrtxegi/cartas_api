from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings


class ParticipantJWTAuthentication(BaseAuthentication):
    """
    Acepta tokens con claim {"type":"participant"}.
    No intenta resolver un usuario Django (CustomUser).
    Deja request.user = AnonymousUser y request.auth = payload (dict).
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b"bearer":
            return None  # no hay token -> que prueben otros auth backends

        if len(auth) == 1:
            raise AuthenticationFailed("Invalid Authorization header. No credentials provided.")
        if len(auth) > 2:
            raise AuthenticationFailed("Invalid Authorization header. Token string should not contain spaces.")

        raw_token = auth[1].decode("utf-8")

        token_backend = TokenBackend(
            algorithm=api_settings.ALGORITHM,
            signing_key=api_settings.SIGNING_KEY,
            verifying_key=api_settings.VERIFYING_KEY,
            audience=api_settings.AUDIENCE,
            issuer=api_settings.ISSUER,
            jwk_url=api_settings.JWK_URL,
            leeway=api_settings.LEEWAY,
        )

        try:
            payload = token_backend.decode(raw_token, verify=True)
        except TokenError:
            raise AuthenticationFailed("Token is invalid or expired.")
        except Exception:
            raise AuthenticationFailed("Token decode failed.")

        # Solo aceptamos los tokens de participant aquí
        if payload.get("type") != "participant":
            return None

        return (AnonymousUser(), payload)
