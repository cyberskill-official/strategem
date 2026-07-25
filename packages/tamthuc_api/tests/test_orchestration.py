from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_api.clients.rag import StubRagClient
from tamthuc_api.clients.rule import StubRuleClient
from tamthuc_api.orchestrator import NINE_STEPS, Orchestrator


def _auth_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.setenv(
        "TAMTHUC_AUTH_JWT_SECRET",
        "test-jwt-secret-at-least-32-bytes-long!!",
    )
    from tamthuc_auth.config import reset_settings_cache

    reset_settings_cache()
    return TestClient(create_app())


def _register_login(client: TestClient, email: str, *, tier: str = "free") -> str:
    client.post("/auth/register", json={"email": email, "password": "password123"})
    login = client.post("/auth/login", json={"email": email, "password": "password123"})
    assert login.status_code == 200, login.text
    token = login.json()["access"]
    if tier != "free":
        svc = client.app.state.auth_service  # type: ignore[attr-defined]
        user = svc.store.get_by_email(email)
        assert user is not None
        user.tier = tier
        svc.store.update(user)
        # re-issue access with updated tier claim
        from tamthuc_auth.tokens import issue_access

        token = str(issue_access(str(user.id), tier, settings=svc.settings))
    return str(token)


def test_qimen_nine_step_sequence_and_passthrough() -> None:
    rule = StubRuleClient()
    rag = StubRagClient()
    orch = Orchestrator(rule=rule, rag=rag)
    client = TestClient(create_app(orch))
    r = client.post(
        "/api/v1/calculate/qimen",
        json={"datetime": "2004-01-01T10:30:00", "longitude": 106.7, "question": "q"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ai_disclosure"]["is_ai_generated"] is True
    assert "qimen" in body["charts"]
    assert body["charts"]["qimen"]["envelope_version"] == 1
    # Full nine-step call order (TASK-API-001)
    assert orch.call_log == list(NINE_STEPS)
    assert rule.last_envelope is not None
    assert rag.last_envelope == rule.last_envelope
    assert body["charts"]["qimen"] is not None


def test_calculate_all_requires_jwt(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _auth_client(monkeypatch)
    r = client.post(
        "/api/v1/calculate/all",
        json={"datetime": "2004-01-01T10:30:00", "tier": "premium"},
    )
    assert r.status_code == 401


def test_calculate_all_forbidden_for_free_jwt(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _auth_client(monkeypatch)
    token = _register_login(client, "free-all@example.com", tier="free")
    r = client.post(
        "/api/v1/calculate/all",
        headers={"Authorization": f"Bearer {token}"},
        json={"datetime": "2004-01-01T10:30:00", "tier": "premium"},
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "FORBIDDEN_TIER"


def test_calculate_all_premium_jwt(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _auth_client(monkeypatch)
    token = _register_login(client, "prem-all@example.com", tier="premium")
    r = client.post(
        "/api/v1/calculate/all",
        headers={"Authorization": f"Bearer {token}"},
        json={"datetime": "2004-01-01T10:30:00"},
    )
    assert r.status_code == 200, r.text
    assert set(r.json()["charts"]) == {"qimen", "liuren", "taiyi"}
