"""FR-AUTH-004 erasure tests."""

from __future__ import annotations

import time

import pytest
from tamthuc_auth.config import get_settings
from tamthuc_auth.crypto import decrypt_birth_data, encrypt_birth_data
from tamthuc_auth.dsar import DsarService, FreshAuthRequired
from tamthuc_auth.erasure import erase_user_data
from tamthuc_auth.passwords import hash_password
from tamthuc_auth.store import InMemoryUserStore, new_user


def test_crypto_shred() -> None:
    store = InMemoryUserStore()
    mk = get_settings().master_key()
    env = encrypt_birth_data({"date": "1990-01-01", "place": "HN"}, mk)
    u = store.create(
        new_user("e@ex.com", password_hash=hash_password("p"), birth_data_envelope=env)
    )
    # pre: decrypt works
    assert decrypt_birth_data(env, mk)["date"] == "1990-01-01"
    result = erase_user_data(str(u.id), store=store, master_key=mk)
    assert result.crypto_shredded is True
    user = store.get_by_id(u.id)
    assert user is not None
    assert user.preferences.get("deleted_at")
    with pytest.raises((ValueError, TypeError, KeyError, OSError)):
        decrypt_birth_data(user.birth_data_envelope or {}, mk)


def test_retention_and_idempotent() -> None:
    store = InMemoryUserStore()
    mk = get_settings().master_key()
    u = store.create(new_user("f@ex.com", password_hash=hash_password("p")))
    erased: set[str] = set()
    r1 = erase_user_data(str(u.id), store=store, master_key=mk, already_erased=erased)
    assert any(x["table"] == "audit" for x in r1.retained)
    r2 = erase_user_data(str(u.id), store=store, master_key=mk, already_erased=erased)
    assert r2.idempotent_replay is True


def test_dsar_erase_fresh_auth() -> None:
    store = InMemoryUserStore()
    mk = get_settings().master_key()
    u = store.create(new_user("g@ex.com", password_hash=hash_password("p")))
    svc = DsarService(store, mk)
    with pytest.raises(FreshAuthRequired):
        svc.erase(str(u.id), auth_iat=None)
    r = svc.erase(str(u.id), auth_iat=time.time())
    assert r.crypto_shredded
    assert any(a["action"] == "dsar_erase" for a in svc._audit)
    assert "payload" not in svc._audit[0]
