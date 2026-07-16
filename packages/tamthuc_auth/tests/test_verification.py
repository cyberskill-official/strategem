"""TASK-AUTH-003 email verification tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from tamthuc_auth.email import FakeEmailSender
from tamthuc_auth.store import InMemoryUserStore, new_user
from tamthuc_auth.token_store import EmailTokenStore, hash_token
from tamthuc_auth.verification import (
    GENERIC_OK,
    VerificationError,
    confirm_verification,
    issue_verification,
    request_verification_by_email,
)


@pytest.fixture
def env() -> tuple[InMemoryUserStore, EmailTokenStore, FakeEmailSender]:
    store = InMemoryUserStore()
    tokens = EmailTokenStore()
    mail = FakeEmailSender()
    return store, tokens, mail


def test_issue_confirm_happy(
    env: tuple[InMemoryUserStore, EmailTokenStore, FakeEmailSender],
) -> None:
    store, tokens, mail = env
    u = store.create(new_user("a@example.com", password_hash="x", email_verified=False))
    issue_verification(str(u.id), store=store, tokens=tokens, mail=mail)
    assert len(mail.sent) == 1
    raw = mail.sent[0]["_raw"]["token"]
    # hashed at rest — raw not in store structures
    assert raw not in str(tokens._rows)
    assert hash_token(raw) in tokens._by_hash
    out = confirm_verification(raw, store=store, tokens=tokens)
    assert out["email_verified"] is True
    assert store.get_by_id(u.id) is not None
    assert store.get_by_id(u.id).email_verified is True  # type: ignore[union-attr]


def test_single_use(env: tuple[InMemoryUserStore, EmailTokenStore, FakeEmailSender]) -> None:
    store, tokens, mail = env
    u = store.create(new_user("b@example.com", password_hash="x"))
    issue_verification(str(u.id), store=store, tokens=tokens, mail=mail)
    raw = mail.sent[0]["_raw"]["token"]
    confirm_verification(raw, store=store, tokens=tokens)
    with pytest.raises(VerificationError):
        confirm_verification(raw, store=store, tokens=tokens)


def test_reissue_invalidates_prior(
    env: tuple[InMemoryUserStore, EmailTokenStore, FakeEmailSender],
) -> None:
    store, tokens, mail = env
    u = store.create(new_user("c@example.com", password_hash="x"))
    issue_verification(str(u.id), store=store, tokens=tokens, mail=mail)
    old = mail.sent[0]["_raw"]["token"]
    issue_verification(str(u.id), store=store, tokens=tokens, mail=mail)
    new = mail.sent[1]["_raw"]["token"]
    with pytest.raises(VerificationError):
        confirm_verification(old, store=store, tokens=tokens)
    confirm_verification(new, store=store, tokens=tokens)


def test_enumeration_safe_request(
    env: tuple[InMemoryUserStore, EmailTokenStore, FakeEmailSender],
) -> None:
    store, tokens, mail = env
    store.create(new_user("known@example.com", password_hash="x"))
    a = request_verification_by_email("known@example.com", store=store, tokens=tokens, mail=mail)
    b = request_verification_by_email("unknown@example.com", store=store, tokens=tokens, mail=mail)
    assert a == b == GENERIC_OK


def test_expired_token(env: tuple[InMemoryUserStore, EmailTokenStore, FakeEmailSender]) -> None:
    store, tokens, mail = env
    u = store.create(new_user("d@example.com", password_hash="x"))
    issue_verification(str(u.id), store=store, tokens=tokens, mail=mail, ttl_s=-1)
    raw = mail.sent[0]["_raw"]["token"]
    with pytest.raises(VerificationError):
        confirm_verification(raw, store=store, tokens=tokens)


def test_no_plaintext_column(
    env: tuple[InMemoryUserStore, EmailTokenStore, FakeEmailSender],
) -> None:
    store, tokens, mail = env
    u = store.create(new_user(f"{uuid4()}@ex.com", password_hash="x"))
    issue_verification(str(u.id), store=store, tokens=tokens, mail=mail)
    assert tokens.has_plaintext() is False
