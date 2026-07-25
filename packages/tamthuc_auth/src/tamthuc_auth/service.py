"""Auth use-cases: register, login, social, refresh, me."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from tamthuc_auth.config import AuthSettings, get_settings
from tamthuc_auth.crypto import encrypt_birth_data
from tamthuc_auth.errors import InvalidCredentials, SocialTokenInvalid
from tamthuc_auth.models import (
    BirthData,
    CurrentUser,
    MeResponse,
    RegisterResponse,
    TokenPair,
    UserRecord,
)
from tamthuc_auth.passwords import hash_password, verify_password
from tamthuc_auth.social import IdTokenVerifier, JwtIdTokenVerifier
from tamthuc_auth.store import InMemoryUserStore, UserStore, new_user
from tamthuc_auth.tokens import (
    RevocationStore,
    TokenService,
    get_revocation_store,
    issue_access,
    issue_refresh,
    issue_token_pair,
    revoke_refresh,
    verify_access,
    verify_refresh,
)

log = logging.getLogger("tamthuc_auth.service")

# Verification event sink for TASK-AUTH-003 (emit only; no delivery here).
_verification_events: list[dict[str, Any]] = []

# Precomputed argon2 hash so missing-user path still runs verify (no enumeration).
_DUMMY_HASH = hash_password("dummy-not-a-real-password-value")


def drain_verification_events() -> list[dict[str, Any]]:
    out = list(_verification_events)
    _verification_events.clear()
    return out


class AuthService:
    def __init__(
        self,
        store: UserStore | None = None,
        settings: AuthSettings | None = None,
        tokens: TokenService | None = None,
        social: IdTokenVerifier | None = None,
        revocation: RevocationStore | Any | None = None,
    ) -> None:
        self.store = store or InMemoryUserStore()
        self.settings = settings or get_settings()
        self.revocation = revocation or get_revocation_store()
        self.tokens = tokens or TokenService(settings=self.settings, store=self.revocation)
        self.social = social or JwtIdTokenVerifier(self.settings)

    def register(
        self,
        email: str,
        password: str,
        birth_data: BirthData | dict[str, Any] | None = None,
    ) -> RegisterResponse:
        log.info("auth.register.start", extra={"email_domain": email.split("@")[-1]})
        envelope = None
        if birth_data is not None:
            plain = (
                birth_data.model_dump() if isinstance(birth_data, BirthData) else dict(birth_data)
            )
            envelope = encrypt_birth_data(plain, self.settings.master_key())
            if any(k in envelope for k in ("date", "time", "place")):
                raise RuntimeError("plaintext leaked into envelope")
        user = new_user(
            email,
            password_hash=hash_password(password),
            birth_data_envelope=envelope,
            email_verified=False,
        )
        created = self.store.create(user)
        _verification_events.append(
            {
                "type": "email.verification.requested",
                "user_id": str(created.id),
                "email": created.email,
            }
        )
        log.info("auth.register.ok", extra={"user_id": str(created.id), "email_verified": False})
        return RegisterResponse(user_id=created.id, email_verified=False)

    def login(self, email: str, password: str) -> TokenPair:
        user = self.store.get_by_email(email)
        ok = False
        if user is not None and user.password_hash:
            ok = verify_password(password, user.password_hash)
        else:
            verify_password(password, _DUMMY_HASH)
        if not ok or user is None:
            log.info("auth.login.fail")
            raise InvalidCredentials()
        pair = issue_token_pair(str(user.id), user.tier, settings=self.settings)
        log.info("auth.login.ok", extra={"user_id": str(user.id)})
        return TokenPair(access=pair["access"], refresh=pair["refresh"])

    def login_social(self, provider: str, id_token: str) -> TokenPair:
        try:
            identity = self.social.verify(provider, id_token)
        except SocialTokenInvalid:
            raise
        except Exception as e:
            raise SocialTokenInvalid() from e
        user = self.store.get_by_email(identity.email)
        if user is None:
            user = new_user(
                identity.email,
                password_hash=None,
                email_verified=identity.email_verified,
                social_provider=identity.provider,
                social_subject=identity.subject,
            )
            user = self.store.create(user)
            log.info(
                "auth.social.provisioned",
                extra={"provider": provider, "user_id": str(user.id)},
            )
        elif user.social_provider is None:
            user = user.model_copy(
                update={
                    "social_provider": identity.provider,
                    "social_subject": identity.subject,
                    "email_verified": user.email_verified or identity.email_verified,
                }
            )
            user = self.store.update(user)
        pair = issue_token_pair(str(user.id), user.tier, settings=self.settings)
        return TokenPair(access=pair["access"], refresh=pair["refresh"])

    def refresh(self, refresh_token: str) -> TokenPair:
        claims = verify_refresh(refresh_token, settings=self.settings, store=self.revocation)
        revoke_refresh(claims.jti, store=self.revocation, exp=float(claims.exp))
        user = self.store.get_by_id(UUID(claims.sub))
        tier = user.tier if user else "free"
        pair = {
            "access": issue_access(claims.sub, tier, settings=self.settings),
            "refresh": issue_refresh(claims.sub, settings=self.settings),
        }
        log.info("auth.refresh.ok", extra={"user_id": claims.sub})
        return TokenPair(access=pair["access"], refresh=pair["refresh"])

    def me(self, access_token: str) -> MeResponse:
        claims = verify_access(access_token, settings=self.settings)
        user = self.store.get_by_id(UUID(claims.sub))
        if user is None:
            raise InvalidCredentials()
        return MeResponse(
            user_id=user.id,
            email=user.email,
            tier=user.tier,
            preferences=user.preferences,
            email_verified=user.email_verified,
        )

    def current_user(self, access_token: str) -> CurrentUser:
        claims = verify_access(access_token, settings=self.settings)
        user = self.store.get_by_id(UUID(claims.sub))
        if user is None:
            raise InvalidCredentials()
        return CurrentUser(
            id=user.id,
            email=user.email,
            tier=user.tier,
            email_verified=user.email_verified,
            preferences=user.preferences,
        )

    def get_user(self, user_id: UUID) -> UserRecord | None:
        return self.store.get_by_id(user_id)
