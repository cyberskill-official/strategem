from __future__ import annotations

from uuid import uuid4

from auth_helpers import auth_header, register_and_login
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app


def test_not_found_envelope() -> None:
    c = TestClient(create_app())
    tokens = register_and_login(c, email="err@example.com")
    # Non-UUID path id → clean 404 (no Postgres round-trip / no driver leak)
    r = c.get("/api/v1/reports/missing", headers=auth_header(tokens["access"]))
    assert r.status_code == 404
    err = r.json()["error"]
    assert err["code"] == "NOT_FOUND"
    assert "request_id" in err
    assert "psycopg" not in r.text.lower()
    assert "uuid" not in err["message"].lower() or "not found" in err["message"].lower()


def test_not_found_valid_uuid_missing() -> None:
    c = TestClient(create_app())
    tokens = register_and_login(c, email="err2@example.com")
    rid = str(uuid4())
    r = c.get(f"/api/v1/reports/{rid}", headers=auth_header(tokens["access"]))
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_timing_optimize_requires_body() -> None:
    """COV-007: timing is productized — empty body is validation (422), not 501 stub."""
    c = TestClient(create_app())
    tokens = register_and_login(c, email="timing-body@example.com", tier="premium")
    r = c.post("/api/v1/timing/optimize", headers=auth_header(tokens["access"]))
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body or (body.get("error") or {}).get("code") in {
        "VALIDATION_ERROR",
        "NOT_IMPLEMENTED",
    }


def test_validation_error() -> None:
    c = TestClient(create_app())
    r = c.post("/api/v1/calculate/qimen", json={"longitude": 999})
    assert r.status_code == 422  # pydantic validation


def test_unhandled_exception_does_not_leak(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """TT-009: catch-all returns generic message + request_id, not str(exc)."""
    from tamthuc_api.app import create_app as _create

    app = _create()

    @app.get("/__boom")
    def boom() -> None:
        raise RuntimeError("secret driver detail CONTEXT: portal $1")

    # Bypass auth for this diagnostic route by temporarily disabling REQUIRE_AUTH
    monkeypatch.setenv("REQUIRE_AUTH", "0")
    c = TestClient(app, raise_server_exceptions=False)
    r = c.get("/__boom")
    assert r.status_code == 500
    err = r.json()["error"]
    assert err["code"] == "INTERNAL"
    assert "secret driver" not in err["message"]
    assert "portal" not in err["message"]
    assert err.get("request_id")
