"""Social OIDC id-token verification (Authlib-style; stubbable for tests).

Production: wire Authlib against Google/Apple discovery. MVP verifies a signed JWT
id_token with configured audience + issuer, matching FR-AUTH-001 verification rules.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Protocol

from jose import JWTError, jwt  # type: ignore[import-untyped]

from tamthuc_auth.config import AuthSettings, get_settings
from tamthuc_auth.errors import SocialTokenInvalid

log = logging.getLogger("tamthuc_auth.social")


@dataclass(frozen=True)
class SocialIdentity:
    provider: str  # google | apple
    subject: str
    email: str
    email_verified: bool = True


class IdTokenVerifier(Protocol):
    def verify(self, provider: str, id_token: str) -> SocialIdentity: ...


class JwtIdTokenVerifier:
    """Verify provider id tokens signed with a known secret/key (test + MVP).

    In production, replace key material with JWKS from OIDC discovery (Authlib).
    """

    def __init__(
        self, settings: AuthSettings | None = None, *, shared_secret: str | None = None
    ) -> None:
        self.settings = settings or get_settings()
        # For tests we sign with the same jwt_secret; production uses provider JWKS.
        self.shared_secret = shared_secret or self.settings.jwt_secret

    def verify(self, provider: str, id_token: str) -> SocialIdentity:
        provider = provider.lower()
        if provider not in ("google", "apple"):
            raise SocialTokenInvalid()
        audience = (
            self.settings.google_audience if provider == "google" else self.settings.apple_audience
        )
        issuer = f"https://accounts.{provider}.test"
        try:
            payload: dict[str, Any] = jwt.decode(
                id_token,
                self.shared_secret,
                algorithms=["HS256"],
                audience=audience,
                issuer=issuer,
                options={"require_exp": True, "require_sub": True},
            )
        except JWTError as e:
            log.info("social.verify_failed", extra={"provider": provider, "err": type(e).__name__})
            raise SocialTokenInvalid() from e
        email = payload.get("email")
        if not email or not isinstance(email, str):
            raise SocialTokenInvalid()
        return SocialIdentity(
            provider=provider,
            subject=str(payload["sub"]),
            email=email.lower(),
            email_verified=bool(payload.get("email_verified", True)),
        )


def mint_test_id_token(
    *,
    provider: str,
    email: str,
    subject: str = "social-sub-1",
    audience: str | None = None,
    issuer: str | None = None,
    secret: str | None = None,
    exp_delta: int = 3600,
    settings: AuthSettings | None = None,
) -> str:
    """Test helper: mint a provider-shaped id_token."""
    s = settings or get_settings()
    provider = provider.lower()
    aud = audience or (s.google_audience if provider == "google" else s.apple_audience)
    iss = issuer or f"https://accounts.{provider}.test"
    now = int(time.time())
    claims = {
        "sub": subject,
        "email": email,
        "email_verified": True,
        "aud": aud,
        "iss": iss,
        "iat": now,
        "exp": now + exp_delta,
    }
    return str(jwt.encode(claims, secret or s.jwt_secret, algorithm="HS256"))
