"""Email dispatch seam — TASK-AUTH-001 / AUTH-003.

Local/test: FakeEmailSender (in-memory, no network).
When ``RESEND_API_KEY`` is set: ResendEmailSender.
Production/staging without Resend (and without explicit fake allow): fail closed.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx

from tamthuc_auth.config import is_local_or_test_env
from tamthuc_auth.errors import AuthError

log = logging.getLogger("tamthuc_auth.email")

RESEND_API_URL = "https://api.resend.com/emails"


class EmailNotConfigured(AuthError):
    """Transactional email required but no sender is configured."""

    code = "email_not_configured"
    http_status = 503

    def __init__(self) -> None:
        super().__init__("email delivery is not configured")


class EmailSendFailed(AuthError):
    code = "email_send_failed"
    http_status = 502

    def __init__(self, message: str = "email delivery failed") -> None:
        super().__init__(message)


class EmailSender(Protocol):
    def send(self, template: str, to: str, context: dict[str, Any]) -> None: ...


@dataclass
class FakeEmailSender:
    """In-memory sink for local/test; never hits a network."""

    sent: list[dict[str, Any]] = field(default_factory=list)

    def send(self, template: str, to: str, context: dict[str, Any]) -> None:
        # never log the raw token field if present — tests assert this
        safe = {k: v for k, v in context.items() if k != "token"}
        self.sent.append({"template": template, "to": to, "context": safe, "_raw": context})


_TEMPLATE_SUBJECT: dict[str, str] = {
    "email_verify": "Verify your TamThuc email",
    "password_reset": "Reset your TamThuc password",
}


def _render_body(template: str, context: dict[str, Any]) -> str:
    token = str(context.get("token") or "")
    if template == "email_verify":
        return (
            "<p>Confirm your email for TamThuc.</p>"
            f"<p>Verification token: <code>{token}</code></p>"
            "<p>If you did not create an account, ignore this message.</p>"
        )
    if template == "password_reset":
        return (
            "<p>Reset your TamThuc password.</p>"
            f"<p>Reset token: <code>{token}</code></p>"
            "<p>If you did not request a reset, ignore this message.</p>"
        )
    return f"<p>TamThuc notification ({template}).</p>"


@dataclass
class ResendEmailSender:
    """Resend.com adapter — used when ``RESEND_API_KEY`` is present."""

    api_key: str
    from_address: str
    client: httpx.Client | None = None

    def send(self, template: str, to: str, context: dict[str, Any]) -> None:
        subject = _TEMPLATE_SUBJECT.get(template, f"TamThuc: {template}")
        payload = {
            "from": self.from_address,
            "to": [to],
            "subject": subject,
            "html": _render_body(template, context),
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            if self.client is not None:
                resp = self.client.post(RESEND_API_URL, json=payload, headers=headers)
            else:
                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(RESEND_API_URL, json=payload, headers=headers)
        except httpx.HTTPError as e:
            log.error("email.resend.transport_error", extra={"template": template})
            raise EmailSendFailed() from e
        if resp.status_code >= 400:
            log.error(
                "email.resend.http_error",
                extra={"template": template, "status": resp.status_code},
            )
            raise EmailSendFailed()
        log.info("email.resend.sent", extra={"template": template})


_default: EmailSender | None = None


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _resend_from_env() -> ResendEmailSender | None:
    api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
    if not api_key:
        return None
    from_addr = (
        os.environ.get("RESEND_FROM") or os.environ.get("RESEND_FROM_ADDRESS") or ""
    ).strip()
    if not from_addr:
        raise EmailNotConfigured()
    return ResendEmailSender(api_key=api_key, from_address=from_addr)


def resolve_email_sender() -> EmailSender:
    """Pick Fake (local/test), Resend (key set), or fail closed in prod/staging."""
    if _env_flag("AUTH_EMAIL_FAKE"):
        return FakeEmailSender()

    resend = _resend_from_env()
    if resend is not None:
        return resend

    if is_local_or_test_env() or _env_flag("ALLOW_FAKE_EMAIL"):
        return FakeEmailSender()

    raise EmailNotConfigured()


def get_email_sender() -> EmailSender:
    global _default
    if _default is None:
        _default = resolve_email_sender()
    return _default


def set_email_sender(sender: EmailSender | None) -> None:
    """Override the process-default sender (tests / wiring)."""
    global _default
    _default = sender


def reset_email_sender() -> FakeEmailSender:
    """Reset to a fresh FakeEmailSender (tests)."""
    fake = FakeEmailSender()
    set_email_sender(fake)
    return fake


def require_transactional_email() -> EmailSender:
    """Fail closed when transactional email is required and unavailable."""
    return get_email_sender()


__all__ = [
    "EmailNotConfigured",
    "EmailSendFailed",
    "EmailSender",
    "FakeEmailSender",
    "ResendEmailSender",
    "get_email_sender",
    "require_transactional_email",
    "reset_email_sender",
    "resolve_email_sender",
    "set_email_sender",
]
