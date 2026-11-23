import time
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError

from app.core.errors import AppError
from app.core.security import SigningKey, TokenVerifier
from tests.support import AUDIENCE, ISSUER, SUPABASE_URL, TokenFactory

LEGACY_SECRET = "legacy-shared-secret-used-only-in-tests-0123456789"  # noqa: S105
OTHER_SECRET = "some-other-secret-that-is-long-enough-0123456789"  # noqa: S105


@pytest.fixture
def factory() -> TokenFactory:
    return TokenFactory()


def assert_unauthenticated(verifier: TokenVerifier, token: str) -> None:
    with pytest.raises(AppError) as error:
        verifier.verify(token)
    assert error.value.status_code == 401
    assert error.value.code == "UNAUTHENTICATED"


def make_legacy_token(secret: str = LEGACY_SECRET, **claim_overrides: Any) -> str:
    issued_at = int(time.time())
    claims = {
        "sub": "legacy-user",
        "aud": AUDIENCE,
        "iss": ISSUER,
        "exp": issued_at + 3600,
        **claim_overrides,
    }
    return jwt.encode(claims, secret, algorithm="HS256")


def test_valid_token_returns_claims(factory: TokenFactory) -> None:
    claims = factory.build_verifier().verify(factory.make_token(subject="abc", email="a@b.ie"))

    assert claims["sub"] == "abc"
    assert claims["email"] == "a@b.ie"


def test_expired_token_is_rejected(factory: TokenFactory) -> None:
    token = factory.make_token(exp=int(time.time()) - 10)

    assert_unauthenticated(factory.build_verifier(), token)


def test_wrong_audience_is_rejected(factory: TokenFactory) -> None:
    assert_unauthenticated(factory.build_verifier(), factory.make_token(aud="anon"))


def test_wrong_issuer_is_rejected(factory: TokenFactory) -> None:
    token = factory.make_token(iss="https://other-project.supabase.co/auth/v1")

    assert_unauthenticated(factory.build_verifier(), token)


@pytest.mark.parametrize("missing_claim", ["exp", "sub", "aud", "iss"])
def test_token_missing_a_required_claim_is_rejected(
    factory: TokenFactory, missing_claim: str
) -> None:
    token = factory.make_token(**{missing_claim: None})

    assert_unauthenticated(factory.build_verifier(), token)


def test_empty_subject_is_rejected(factory: TokenFactory) -> None:
    assert_unauthenticated(factory.build_verifier(), factory.make_token(subject=""))


def test_token_signed_by_another_key_is_rejected(factory: TokenFactory) -> None:
    attacker_key = ec.generate_private_key(ec.SECP256R1())

    assert_unauthenticated(factory.build_verifier(), factory.make_token(signing_key=attacker_key))


def test_malformed_token_is_rejected(factory: TokenFactory) -> None:
    assert_unauthenticated(factory.build_verifier(), "not-a-jwt")


def test_unsigned_token_is_rejected(factory: TokenFactory) -> None:
    unsigned = jwt.encode(
        {"sub": "x", "aud": AUDIENCE, "iss": ISSUER, "exp": int(time.time()) + 60},
        key="",
        algorithm="none",
    )

    assert_unauthenticated(factory.build_verifier(), unsigned)


def test_hs256_token_is_rejected_when_no_legacy_secret_is_configured(
    factory: TokenFactory,
) -> None:
    assert_unauthenticated(factory.build_verifier(), make_legacy_token())


def test_hs256_token_is_accepted_with_the_legacy_secret(factory: TokenFactory) -> None:
    verifier = factory.build_verifier(jwt_secret=LEGACY_SECRET)

    assert verifier.verify(make_legacy_token())["sub"] == "legacy-user"


def test_hs256_token_with_the_wrong_secret_is_rejected(factory: TokenFactory) -> None:
    verifier = factory.build_verifier(jwt_secret=LEGACY_SECRET)
    forged = make_legacy_token(secret=OTHER_SECRET)

    assert_unauthenticated(verifier, forged)


def test_asymmetric_tokens_still_work_when_a_legacy_secret_is_set(factory: TokenFactory) -> None:
    verifier = factory.build_verifier(jwt_secret=LEGACY_SECRET)

    assert verifier.verify(factory.make_token(subject="abc"))["sub"] == "abc"


class FailingResolver:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def get_signing_key_from_jwt(self, token: str) -> SigningKey:
        raise self._error


def test_unknown_signing_key_is_rejected(factory: TokenFactory) -> None:
    verifier = TokenVerifier(
        supabase_url=SUPABASE_URL,
        jwk_client=FailingResolver(PyJWKClientError("Unable to find a signing key")),
    )

    assert_unauthenticated(verifier, factory.make_token())


def test_unreachable_jwks_endpoint_is_reported_as_unavailable_not_unauthenticated(
    factory: TokenFactory,
) -> None:
    verifier = TokenVerifier(
        supabase_url=SUPABASE_URL,
        jwk_client=FailingResolver(PyJWKClientConnectionError("connection refused")),
    )

    with pytest.raises(AppError) as error:
        verifier.verify(factory.make_token())

    assert error.value.status_code == 503
    assert error.value.code == "AUTH_UNAVAILABLE"


def test_issuer_tolerates_a_trailing_slash_in_the_project_url(factory: TokenFactory) -> None:
    verifier = TokenVerifier(
        supabase_url=f"{SUPABASE_URL}/",
        jwk_client=factory.build_verifier()._jwk_client,
    )

    assert verifier.verify(factory.make_token())["sub"] == "auth-user-1"
