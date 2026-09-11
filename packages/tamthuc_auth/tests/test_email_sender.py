"""AUTH-001 email sender resolution — fake, Resend, fail-closed."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

import httpx
import pytest
from tamthuc_auth.email import (
    EmailNotConfigured,
    FakeEmailSender,
    ResendEmailSender,
    reset_email_sender,
    resolve_email_sender,
    set_email_sender,
)


@pytest.fixture(autouse=True)
def _clean_sender(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("RESEND_FROM", raising=False)
    monkeypatch.delenv("RESEND_FROM_ADDRESS", raising=False)
    monkeypatch.delenv("AUTH_EMAIL_FAKE", raising=False)
    monkeypatch.delenv("ALLOW_FAKE_EMAIL", raising=False)
    set_email_sender(None)
    yield
    reset_email_sender()


def test_local_env_uses_fake(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "test")
    sender = resolve_email_sender()
    assert isinstance(sender, FakeEmailSender)


def test_resend_when_key_and_from(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("RESEND_API_KEY", "re_test_key")
    monkeypatch.setenv("RESEND_FROM", "noreply@example.com")
    sender = resolve_email_sender()
    assert isinstance(sender, ResendEmailSender)
    assert sender.from_address == "noreply@example.com"


def test_production_fail_closed_without_email(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    with pytest.raises(EmailNotConfigured):
        resolve_email_sender()


def test_staging_fail_closed_without_email(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.delenv("ENV", raising=False)
    with pytest.raises(EmailNotConfigured):
        resolve_email_sender()


def test_resend_key_without_from_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("RESEND_API_KEY", "re_test_key")
    with pytest.raises(EmailNotConfigured):
        resolve_email_sender()


def test_auth_email_fake_overrides_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("AUTH_EMAIL_FAKE", "1")
    assert isinstance(resolve_email_sender(), FakeEmailSender)


def test_resend_sender_posts(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        body = json.loads(request.content.decode())
        calls.append({"url": str(request.url), "from": body["from"]})
        assert body["from"] == "noreply@example.com"
        assert body["to"] == ["a@example.com"]
        assert "token-xyz" in body["html"]
        return httpx.Response(200, json={"id": "msg_1"})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    sender = ResendEmailSender(
        api_key="re_test",
        from_address="noreply@example.com",
        client=client,
    )
    sender.send("email_verify", "a@example.com", {"token": "token-xyz"})
    assert len(calls) == 1
