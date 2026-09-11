"""Password reset — TASK-AUTH-003 (enumeration-safe, revokes refresh on confirm)."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from tamthuc_auth.email import EmailSender, get_email_sender
from tamthuc_auth.errors import AuthError
from tamthuc_auth.passwords import hash_password
from tamthuc_auth.sessions import SessionStoreProtocol, get_session_store
from tamthuc_auth.store import UserStore
from tamthuc_auth.token_store import EmailTokenStore, EmailTokenStoreProtocol, get_email_token_store
from tamthuc_auth.tokens import RevocationStore, get_revocation_store, revoke_refresh

log = logging.getLogger("tamthuc_auth.reset")

GENERIC_OK = {
    "status": "ok",
    "message": "If the account exists, a password reset email was sent.",
}


class ResetError(AuthError):
    def __init__(self, message: str = "reset failed") -> None:
        super().__init__(message)


def request_password_reset(
    email: str,
    *,
    store: UserStore,
    tokens: EmailTokenStore | EmailTokenStoreProtocol | None = None,
    mail: EmailSender | None = None,
    ttl_s: int = 3600,
) -> dict[str, Any]:
    """Always return GENERIC_OK — never disclose whether the email exists."""
    tokens = tokens or get_email_token_store()
    mail = mail or get_email_sender()
    user = store.get_by_email(email)
    if user is not None:
        raw = tokens.issue(str(user.id), "password_reset", ttl_s=ttl_s, invalidate_priors=True)
        mail.send(
            "password_reset",
            user.email,
            {"token": raw, "user_id": str(user.id)},
        )
        log.info("auth.reset.issued", extra={"user_id": str(user.id)})
    else:
        log.info("auth.reset.request.unknown")
    return GENERIC_OK


def confirm_password_reset(
    token: str,
    new_password: str,
    *,
    store: UserStore,
    tokens: EmailTokenStore | EmailTokenStoreProtocol | None = None,
    revocation: RevocationStore | Any | None = None,
    sessions: SessionStoreProtocol | None = None,
    active_refresh_jtis: list[str] | None = None,
) -> dict[str, Any]:
    """Validate + consume token; argon2 re-hash password; revoke outstanding refresh."""
    tokens = tokens or get_email_token_store()
    revocation = revocation or get_revocation_store()
    sessions = sessions or get_session_store()
    try:
        rec = tokens.consume(token, "password_reset")
    except ValueError as e:
        raise ResetError(str(e)) from e
    user = store.get_by_id(UUID(rec.user_id))
    if user is None:
        raise ResetError("user_missing")
    user.password_hash = hash_password(new_password)
    store.update(user)
    jtis = list(active_refresh_jtis or [])
    jtis.extend(sessions.revoke_all(rec.user_id))
    for jti in jtis:
        revoke_refresh(jti, store=revocation)
    log.info("auth.reset.confirmed", extra={"user_id": rec.user_id})
    return {"status": "ok", "sessions_revoked": True}
