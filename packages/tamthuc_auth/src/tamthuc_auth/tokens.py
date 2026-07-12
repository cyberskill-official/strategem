"""JWT access + revocable refresh tokens (PyJWT / cryptography)."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel, ConfigDict

from tamthuc_auth.config import AuthSettings, get_settings
from tamthuc_auth.errors import TokenExpired, TokenInvalid, TokenRevoked

log = logging.getLogger("tamthuc_auth.tokens")


class AccessClaims(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sub: str
    tier: str
    iat: int
    exp: int
    jti: str
    typ: str = "access"


class RefreshClaims(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sub: str
    iat: int
    exp: int
    jti: str
    typ: str = "refresh"


class RevocationStore:
    """In-process jti denylist; replace with Redis/DB in FR-AUTH-003 multi-device work."""

    def __init__(self) -> None:
        self._revoked: dict[str, float] = {}  # jti -> exp

    def revoke(self, jti: str, exp: float | None = None) -> None:
        self._revoked[jti] = exp if exp is not None else time.time() + 86400 * 30
        log.info("refresh.revoked", extra={"jti": jti})

    def is_revoked(self, jti: str) -> bool:
        exp = self._revoked.get(jti)
        if exp is None:
            return False
        if exp < time.time():
            del self._revoked[jti]
            return False
        return True

    def clear(self) -> None:
        self._revoked.clear()


_default_store = RevocationStore()


def get_revocation_store() -> RevocationStore:
    return _default_store


def issue_access(
    user_id: str,
    tier: str,
    *,
    settings: AuthSettings | None = None,
    now: int | None = None,
) -> str:
    s = settings or get_settings()
    iat = int(now if now is not None else time.time())
    exp = iat + s.access_ttl_seconds
    claims = {
        "sub": user_id,
        "tier": tier,
        "iat": iat,
        "exp": exp,
        "jti": str(uuid.uuid4()),
        "typ": "access",
        "iss": s.issuer,
    }
    return jwt.encode(claims, s.jwt_secret, algorithm=s.jwt_algorithm)


def issue_refresh(
    user_id: str,
    *,
    settings: AuthSettings | None = None,
    now: int | None = None,
) -> str:
    s = settings or get_settings()
    iat = int(now if now is not None else time.time())
    exp = iat + s.refresh_ttl_seconds
    claims = {
        "sub": user_id,
        "iat": iat,
        "exp": exp,
        "jti": str(uuid.uuid4()),
        "typ": "refresh",
        "iss": s.issuer,
    }
    return jwt.encode(claims, s.jwt_secret, algorithm=s.jwt_algorithm)


def verify_access(
    token: str,
    *,
    settings: AuthSettings | None = None,
) -> AccessClaims:
    s = settings or get_settings()
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            s.jwt_secret,
            algorithms=[s.jwt_algorithm],
            options={"require": ["exp", "iat", "sub"]},
        )
    except ExpiredSignatureError as e:
        raise TokenExpired() from e
    except InvalidTokenError as e:
        raise TokenInvalid("token invalid") from e
    if payload.get("typ") != "access":
        raise TokenInvalid("wrong token type")
    try:
        return AccessClaims(
            sub=str(payload["sub"]),
            tier=str(payload.get("tier", "free")),
            iat=int(payload["iat"]),
            exp=int(payload["exp"]),
            jti=str(payload.get("jti", "")),
            typ="access",
        )
    except Exception as e:
        raise TokenInvalid("token claims invalid") from e


def verify_refresh(
    token: str,
    *,
    settings: AuthSettings | None = None,
    store: RevocationStore | None = None,
) -> RefreshClaims:
    s = settings or get_settings()
    rev = store or get_revocation_store()
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            s.jwt_secret,
            algorithms=[s.jwt_algorithm],
            options={"require": ["exp", "iat", "sub"]},
        )
    except ExpiredSignatureError as e:
        raise TokenExpired() from e
    except InvalidTokenError as e:
        raise TokenInvalid("token invalid") from e
    if payload.get("typ") != "refresh":
        raise TokenInvalid("wrong token type")
    jti = str(payload.get("jti", ""))
    if not jti or rev.is_revoked(jti):
        raise TokenRevoked()
    return RefreshClaims(
        sub=str(payload["sub"]),
        iat=int(payload["iat"]),
        exp=int(payload["exp"]),
        jti=jti,
        typ="refresh",
    )


def revoke_refresh(
    jti: str, *, store: RevocationStore | None = None, exp: float | None = None
) -> None:
    (store or get_revocation_store()).revoke(jti, exp=exp)


def issue_token_pair(
    user_id: str,
    tier: str,
    *,
    settings: AuthSettings | None = None,
) -> dict[str, str]:
    return {
        "access": issue_access(user_id, tier, settings=settings),
        "refresh": issue_refresh(user_id, settings=settings),
    }


class TokenService:
    """Thin facade used by routes."""

    def __init__(
        self, settings: AuthSettings | None = None, store: RevocationStore | None = None
    ) -> None:
        self.settings = settings or get_settings()
        self.store = store or get_revocation_store()

    def issue_pair(self, user_id: str, tier: str) -> dict[str, str]:
        return issue_token_pair(user_id, tier, settings=self.settings)

    def rotate_refresh(self, refresh_token: str) -> dict[str, str]:
        claims = verify_refresh(refresh_token, settings=self.settings, store=self.store)
        revoke_refresh(claims.jti, store=self.store, exp=float(claims.exp))
        # tier default free on refresh; caller may reload user
        return {
            "access": issue_access(claims.sub, "free", settings=self.settings),
            "refresh": issue_refresh(claims.sub, settings=self.settings),
        }
