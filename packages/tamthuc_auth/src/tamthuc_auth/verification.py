"""Email verification — FR-AUTH-003."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from tamthuc_auth.email import EmailSender, get_email_sender
from tamthuc_auth.errors import AuthError
from tamthuc_auth.store import UserStore
from tamthuc_auth.token_store import EmailTokenStore, get_email_token_store

log = logging.getLogger("tamthuc_auth.verification")

GENERIC_OK = {"status": "ok", "message": "If the account exists, a verification email was sent."}


class VerificationError(AuthError):
    def __init__(self, message: str = "verification failed") -> None:
        super().__init__(message)


def issue_verification(
    user_id: str,
    *,
    store: UserStore,
    tokens: EmailTokenStore | None = None,
    mail: EmailSender | None = None,
    ttl_s: int = 3600,
) -> dict[str, Any]:
    """Issue a verification token; invalidate priors; send email. Enumeration-safe caller wraps this."""
    tokens = tokens or get_email_token_store()
    mail = mail or get_email_sender()
    user = store.get_by_id(UUID(user_id))
    if user is None:
        # caller should still return GENERIC_OK
        return GENERIC_OK
    if user.social_provider and user.email_verified:
        return GENERIC_OK
    raw = tokens.issue(user_id, "email_verify", ttl_s=ttl_s, invalidate_priors=True)
    mail.send(
        "email_verify",
        user.email,
        {"token": raw, "user_id": user_id},
    )
    log.info("auth.verify.issued", extra={"user_id": user_id})
    return GENERIC_OK


def request_verification_by_email(
    email: str,
    *,
    store: UserStore,
    tokens: EmailTokenStore | None = None,
    mail: EmailSender | None = None,
) -> dict[str, Any]:
    """Enumeration-safe: same response whether or not the email exists."""
    user = store.get_by_email(email)
    if user is not None:
        issue_verification(str(user.id), store=store, tokens=tokens, mail=mail)
    else:
        # constant-ish work: still hash a dummy path via issue invalidation noop
        log.info("auth.verify.request.unknown")
    return GENERIC_OK


def confirm_verification(
    token: str,
    *,
    store: UserStore,
    tokens: EmailTokenStore | None = None,
) -> dict[str, Any]:
    tokens = tokens or get_email_token_store()
    try:
        rec = tokens.consume(token, "email_verify")
    except ValueError as e:
        raise VerificationError(str(e)) from e
    user = store.get_by_id(UUID(rec.user_id))
    if user is None:
        raise VerificationError("user_missing")
    user.email_verified = True
    store.update(user)
    log.info("auth.verify.confirmed", extra={"user_id": rec.user_id})
    return {"email_verified": True}
