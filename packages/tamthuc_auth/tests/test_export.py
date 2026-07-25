"""TASK-AUTH-004 export tests."""

from __future__ import annotations

import time

import pytest
from tamthuc_auth.config import get_settings, reset_settings_cache
from tamthuc_auth.crypto import encrypt_birth_data
from tamthuc_auth.dsar import DsarService, FreshAuthRequired
from tamthuc_auth.export import ArchiveStore, export_user_data
from tamthuc_auth.passwords import hash_password
from tamthuc_auth.store import InMemoryUserStore, new_user


@pytest.fixture(autouse=True)
def _test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "test")
    reset_settings_cache()


def test_export_complete_and_scoped() -> None:
    store = InMemoryUserStore()
    mk = get_settings().master_key()
    u1 = store.create(
        new_user(
            "a@ex.com",
            password_hash=hash_password("p"),
            birth_data_envelope=encrypt_birth_data({"date": "1990-01-01"}, mk),
        )
    )
    u2 = store.create(new_user("b@ex.com", password_hash=hash_password("p")))
    hist = {
        "queries": [
            {"user_id": str(u1.id), "q": "mine"},
            {"user_id": str(u2.id), "q": "foreign"},
        ],
        "charts": [{"user_id": str(u1.id), "id": "c1"}],
        "reports": [],
        "audit": [{"user_id": str(u1.id), "action": "login"}],
    }
    arch = export_user_data(str(u1.id), store=store, master_key=mk, history=hist)
    assert arch.profile["birth_data"] == {"date": "1990-01-01"}
    assert all(r["user_id"] == str(u1.id) for r in arch.queries)
    assert not any(r.get("q") == "foreign" for r in arch.queries)


def test_time_limited_delivery() -> None:
    store = InMemoryUserStore()
    mk = get_settings().master_key()
    u = store.create(new_user("c@ex.com", password_hash=hash_password("p")))
    svc = DsarService(store, mk, archives=ArchiveStore())
    delivery, arch = svc.export(str(u.id), auth_iat=time.time())
    got = svc.archives.get(delivery.archive_ref, delivery.token)
    assert got is not None
    assert svc.archives.get(delivery.archive_ref, "wrong") is None
    # expire
    svc.archives._archives[delivery.archive_ref] = (arch, time.time() - 1, delivery.token)
    assert svc.archives.get(delivery.archive_ref, delivery.token) is None


def test_fresh_auth_required() -> None:
    store = InMemoryUserStore()
    mk = get_settings().master_key()
    u = store.create(new_user("d@ex.com", password_hash=hash_password("p")))
    svc = DsarService(store, mk)
    with pytest.raises(FreshAuthRequired):
        svc.export(str(u.id), auth_iat=time.time() - 10_000)
