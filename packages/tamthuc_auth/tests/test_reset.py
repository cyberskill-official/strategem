"""TASK-AUTH-003 password reset tests."""

from __future__ import annotations

import pytest
from tamthuc_auth.email import FakeEmailSender
from tamthuc_auth.passwords import hash_password, verify_password
from tamthuc_auth.reset import (
    GENERIC_OK,
    ResetError,
    confirm_password_reset,
    request_password_reset,
)
from tamthuc_auth.store import InMemoryUserStore, new_user
from tamthuc_auth.token_store import EmailTokenStore
from tamthuc_auth.tokens import RevocationStore


@pytest.fixture
def env() -> tuple[InMemoryUserStore, EmailTokenStore, FakeEmailSender, RevocationStore]:
    return InMemoryUserStore(), EmailTokenStore(), FakeEmailSender(), RevocationStore()


def test_reset_confirm_rehashes_and_single_use(
    env: tuple[InMemoryUserStore, EmailTokenStore, FakeEmailSender, RevocationStore],
) -> None:
    store, tokens, mail, rev = env
    u = store.create(new_user("r@example.com", password_hash=hash_password("old-pass-1")))
    request_password_reset("r@example.com", store=store, tokens=tokens, mail=mail)
    raw = mail.sent[0]["_raw"]["token"]
    confirm_password_reset(
        raw,
        "new-pass-2-long",
        store=store,
        tokens=tokens,
        revocation=rev,
        active_refresh_jtis=["jti-1", "jti-2"],
    )
    user = store.get_by_id(u.id)
    assert user is not None
    assert verify_password("new-pass-2-long", user.password_hash or "")
    assert not verify_password("old-pass-1", user.password_hash or "")
    assert rev.is_revoked("jti-1")
    assert rev.is_revoked("jti-2")
    with pytest.raises(ResetError):
        confirm_password_reset(raw, "another", store=store, tokens=tokens, revocation=rev)


def test_enumeration_safe(
    env: tuple[InMemoryUserStore, EmailTokenStore, FakeEmailSender, RevocationStore],
) -> None:
    store, tokens, mail, _ = env
    store.create(new_user("known@ex.com", password_hash=hash_password("p")))
    a = request_password_reset("known@ex.com", store=store, tokens=tokens, mail=mail)
    b = request_password_reset("nope@ex.com", store=store, tokens=tokens, mail=mail)
    assert a == b == GENERIC_OK
    assert a.keys() == b.keys()
