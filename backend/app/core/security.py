"""Supabase access-token verification (FR-AUTH-3)."""

from typing import Any, Protocol

import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError

from app.core.errors import AppError, ErrorCode

ASYMMETRIC_ALGORITHMS = ["ES256", "RS256"]
LEGACY_ALGORITHM = "HS256"
AUDIENCE = "authenticated"
JWKS_CACHE_SECONDS = 3600


class SigningKey(Protocol):
    @property
    def key(self) -> Any: ...


class SigningKeyResolver(Protocol):
    def get_signing_key_from_jwt(self, token: str) -> SigningKey: ...


class TokenVerifier:
    """Checks signature, expiry, issuer and audience, then returns the claims.

    Keys come from the project's JWKS endpoint. PyJWKClient caches them for an hour and
    re-fetches once when a token carries an unknown key id, so key rotation does not
    break login. Legacy projects that sign with a shared secret set SUPABASE_JWT_SECRET;
    HS256 tokens are accepted only in that case.
    """

    def __init__(
        self,
        *,
        supabase_url: str,
        jwt_secret: str = "",
        jwk_client: SigningKeyResolver | None = None,
    ) -> None:
        self._issuer = f"{supabase_url.rstrip('/')}/auth/v1"
        self._jwt_secret = jwt_secret
        self._jwk_client: SigningKeyResolver = jwk_client or PyJWKClient(
            f"{self._issuer}/.well-known/jwks.json",
            cache_jwk_set=True,
            lifespan=JWKS_CACHE_SECONDS,
        )

    def verify(self, token: str) -> dict[str, Any]:
        try:
            header = jwt.get_unverified_header(token)
            key: Any
            if self._jwt_secret and header.get("alg") == LEGACY_ALGORITHM:
                key, algorithms = self._jwt_secret, [LEGACY_ALGORITHM]
            else:
                key = self._jwk_client.get_signing_key_from_jwt(token).key
                algorithms = ASYMMETRIC_ALGORITHMS
            claims: dict[str, Any] = jwt.decode(
                token,
                key,
                algorithms=algorithms,
                audience=AUDIENCE,
                issuer=self._issuer,
                options={"require": ["exp", "sub", "aud", "iss"]},
            )
        except PyJWKClientConnectionError as exc:
            raise AppError(
                "AUTH_UNAVAILABLE", "Could not reach the sign-in service", status_code=503
            ) from exc
        except (jwt.InvalidTokenError, PyJWKClientError) as exc:
            raise AppError(ErrorCode.UNAUTHENTICATED, "Invalid or expired token") from exc

        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise AppError(ErrorCode.UNAUTHENTICATED, "Invalid or expired token")
        return claims
