"""Auth use-cases: register, login, social, refresh, me, sessions."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any
from uuid import UUID

from tamthuc_auth.config import AuthSettings, get_settings
from tamthuc_auth.crypto import encrypt_birth_data
from tamthuc_auth.email import EmailSender, require_transactional_email
from tamthuc_auth.errors import InvalidCredentials, SocialTokenInvalid, TokenRevoked
from tamthuc_auth.models import (
    BirthData,
    CurrentUser,
    MeResponse,
    RegisterResponse,
    SessionInfo,
    TokenPair,
    UserRecord,
)
from tamthuc_auth.passwords import hash_password, verify_password
from tamthuc_auth.sessions import (
    InMemorySessionStore,
    SessionReuseError,
    SessionStoreProtocol,
    get_session_store,
)
from tamthuc_auth.social import IdTokenVerifier, JwtIdTokenVerifier
from tamthuc_auth.store import InMemoryUserStore, UserStore, new_user
from tamthuc_auth.token_store import EmailTokenStore, EmailTokenStoreProtocol, get_email_token_store
from tamthuc_auth.tokens import (
    RevocationStore,
    TokenService,
    get_revocation_store,
    issue_access,
    issue_refresh,
    revoke_refresh,
    verify_access,
    verify_refresh,
)
from tamthuc_auth.verification import issue_verification

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
        email_tokens: EmailTokenStore | EmailTokenStoreProtocol | None = None,
        mail: EmailSender | None = None,
        sessions: SessionStoreProtocol | InMemorySessionStore | None = None,
    ) -> None:
        self.store = store or InMemoryUserStore()
        self.settings = settings or get_settings()
        self.revocation = revocation or get_revocation_store()
        self.tokens = tokens or TokenService(settings=self.settings, store=self.revocation)
        self.social = social or JwtIdTokenVerifier(self.settings)
        self.email_tokens = email_tokens or get_email_token_store()
        self.mail = mail
        self.sessions = sessions or get_session_store()

    def register(
        self,
        email: str,
        password: str,
        birth_data: BirthData | dict[str, Any] | None = None,
    ) -> RegisterResponse:
        log.info("auth.register.start", extra={"email_domain": email.split("@")[-1]})
        # Fail closed before create when transactional email is unavailable in prod.
        mail = self.mail or require_transactional_email()
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
        issue_verification(
            str(created.id),
            store=self.store,
            tokens=self.email_tokens,
            mail=mail,
        )
        log.info("auth.register.ok", extra={"user_id": str(created.id), "email_verified": False})
        return RegisterResponse(user_id=created.id, email_verified=False)

    def _issue_session_pair(
        self,
        user_id: str,
        tier: str,
        *,
        label: str | None = None,
    ) -> TokenPair:
        family_id = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())
        now = int(time.time())
        expires_at = float(now + self.settings.refresh_ttl_seconds)
        self.sessions.create(
            user_id,
            refresh_jti,
            expires_at=expires_at,
            label=label,
            family_id=family_id,
        )
        access = issue_access(user_id, tier, settings=self.settings, now=now)
        refresh = issue_refresh(
            user_id,
            settings=self.settings,
            now=now,
            family_id=family_id,
            jti=refresh_jti,
        )
        return TokenPair(access=access, refresh=refresh)

    def logout(self, refresh_token: str) -> dict[str, bool]:
        """Revoke the presented refresh family/jti. Always returns ok (idempotent)."""
        try:
            claims = verify_refresh(refresh_token, settings=self.settings, store=self.revocation)
            revoke_refresh(claims.jti, store=self.revocation, exp=float(claims.exp))
            if claims.fid:
                self.sessions.revoke(claims.fid, user_id=claims.sub)
        except Exception:
            log.info("auth.logout.noop")
        return {"ok": True}

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
        pair = self._issue_session_pair(str(user.id), user.tier)
        log.info("auth.login.ok", extra={"user_id": str(user.id)})
        return pair

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
        return self._issue_session_pair(str(user.id), user.tier, label=f"social:{provider}")

    def refresh(self, refresh_token: str) -> TokenPair:
        # Family tokens: ``current_jti`` is authoritative (enables reuse detection).
        # Legacy tokens without ``fid`` still use the jti denylist.
        claims = verify_refresh(
            refresh_token,
            settings=self.settings,
            store=self.revocation,
            check_revocation=False,
        )
        user = self.store.get_by_id(UUID(claims.sub))
        tier = user.tier if user else "free"
        new_jti = str(uuid.uuid4())
        now = int(time.time())
        expires_at = float(now + self.settings.refresh_ttl_seconds)

        if claims.fid:
            try:
                self.sessions.rotate(
                    claims.fid,
                    claims.jti,
                    new_jti,
                    expires_at=expires_at,
                )
            except SessionReuseError as e:
                fam = self.sessions.get(claims.fid)
                if fam is not None and fam.current_jti:
                    revoke_refresh(fam.current_jti, store=self.revocation, exp=fam.expires_at)
                revoke_refresh(claims.jti, store=self.revocation, exp=float(claims.exp))
                raise TokenRevoked() from e
            family_id = claims.fid
        else:
            if self.revocation.is_revoked(claims.jti):
                raise TokenRevoked()
            revoke_refresh(claims.jti, store=self.revocation, exp=float(claims.exp))
            family_id = str(uuid.uuid4())
            self.sessions.create(
                claims.sub,
                new_jti,
                expires_at=expires_at,
                family_id=family_id,
            )

        pair = {
            "access": issue_access(claims.sub, tier, settings=self.settings, now=now),
            "refresh": issue_refresh(
                claims.sub,
                settings=self.settings,
                now=now,
                family_id=family_id,
                jti=new_jti,
            ),
        }
        log.info("auth.refresh.ok", extra={"user_id": claims.sub, "family_id": family_id})
        return TokenPair(access=pair["access"], refresh=pair["refresh"])

    def list_sessions(self, access_token: str) -> list[SessionInfo]:
        claims = verify_access(access_token, settings=self.settings)
        rows = self.sessions.list_active(claims.sub)
        return [
            SessionInfo(
                id=r.id,
                created_at=r.created_at,
                last_seen_at=r.last_seen_at,
                expires_at=r.expires_at,
                label=r.label,
                current=False,
            )
            for r in rows
        ]

    def revoke_session(self, access_token: str, session_id: str) -> dict[str, bool]:
        claims = verify_access(access_token, settings=self.settings)
        rec = self.sessions.get(session_id)
        if rec is not None and rec.user_id == claims.sub and rec.revoked_at is None:
            revoke_refresh(rec.current_jti, store=self.revocation, exp=rec.expires_at)
        ok = self.sessions.revoke(session_id, user_id=claims.sub)
        return {"ok": ok}

    def revoke_all_sessions(self, access_token: str) -> dict[str, Any]:
        claims = verify_access(access_token, settings=self.settings)
        jtis = self.sessions.revoke_all(claims.sub)
        for jti in jtis:
            revoke_refresh(jti, store=self.revocation)
        return {"ok": True, "revoked": len(jtis)}

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
