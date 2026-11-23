"""Test helpers: locally signed access tokens that go through the real TokenVerifier."""

import time
from types import SimpleNamespace
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric import ec

from app.core.security import SigningKey, TokenVerifier

SUPABASE_URL = "https://test-project.supabase.co"
ISSUER = f"{SUPABASE_URL}/auth/v1"
AUDIENCE = "authenticated"


class StaticKeyResolver:
    """Stands in for the JWKS client: always answers with one public key."""

    def __init__(self, public_key: ec.EllipticCurvePublicKey) -> None:
        self._public_key = public_key

    def get_signing_key_from_jwt(self, token: str) -> SigningKey:
        return SimpleNamespace(key=self._public_key)


class TokenFactory:
    def __init__(self) -> None:
        self.private_key = ec.generate_private_key(ec.SECP256R1())

    def build_verifier(self, *, jwt_secret: str = "") -> TokenVerifier:
        return TokenVerifier(
            supabase_url=SUPABASE_URL,
            jwt_secret=jwt_secret,
            jwk_client=StaticKeyResolver(self.private_key.public_key()),
        )

    def make_token(
        self,
        *,
        subject: str = "auth-user-1",
        email: str | None = "user1@example.com",
        signing_key: ec.EllipticCurvePrivateKey | None = None,
        **claim_overrides: Any,
    ) -> str:
        """A valid token by default. Pass a claim as None to leave it out."""
        issued_at = int(time.time())
        claims: dict[str, Any] = {
            "sub": subject,
            "email": email,
            "aud": AUDIENCE,
            "iss": ISSUER,
            "iat": issued_at,
            "exp": issued_at + 3600,
        }
        claims.update(claim_overrides)
        claims = {name: value for name, value in claims.items() if value is not None}
        return jwt.encode(
            claims,
            signing_key or self.private_key,
            algorithm="ES256",
            headers={"kid": "test-key"},
        )
