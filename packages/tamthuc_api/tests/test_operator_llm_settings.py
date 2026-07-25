"""Operator BYOK LLM settings — admin-only, masked keys, no raw secret leak."""

from __future__ import annotations

from auth_helpers import auth_header, register_and_login
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_api.operator_llm import reset_memory_for_tests


def test_operator_llm_requires_admin(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    reset_memory_for_tests()
    monkeypatch.setenv("ENV", "test")
    client = TestClient(create_app())
    tokens = register_and_login(client, email="user@example.com")
    r = client.get(
        "/api/v1/operator/llm-settings",
        headers=auth_header(tokens["access"]),
    )
    assert r.status_code == 403


def test_operator_llm_admin_roundtrip_masks_key(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    reset_memory_for_tests()
    monkeypatch.setenv("ENV", "test")
    client = TestClient(create_app())
    tokens = register_and_login(client, email="admin-op@example.com")

    # Elevate to admin via auth store
    svc = client.app.state.auth_service
    me = client.get("/auth/me", headers=auth_header(tokens["access"]))
    uid = me.json()["user_id"]
    user = svc.store.get_by_id(__import__("uuid").UUID(uid))
    user.tier = "admin"
    svc.store.update(user)

    secret = "sk-test-never-return-this-raw-value"
    put = client.put(
        "/api/v1/operator/llm-settings",
        headers=auth_header(tokens["access"]),
        json={
            "provider_base_url": "http://127.0.0.1:1234/v1",
            "model_id": "local-model",
            "backend": "openai_compatible",
            "api_key": secret,
        },
    )
    assert put.status_code == 200, put.text
    body = put.json()
    assert body["configured"] is True
    assert body["settings"]["has_api_key"] is True
    assert secret not in put.text
    assert body["settings"]["api_key_masked"] != secret
    assert "api_key" not in body["settings"]

    got = client.get(
        "/api/v1/operator/llm-settings",
        headers=auth_header(tokens["access"]),
    )
    assert got.status_code == 200
    assert secret not in got.text
    assert got.json()["settings"]["model_id"] == "local-model"


def test_unauthenticated_operator_route(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    reset_memory_for_tests()
    client = TestClient(create_app())
    r = client.get("/api/v1/operator/llm-settings")
    assert r.status_code == 401
