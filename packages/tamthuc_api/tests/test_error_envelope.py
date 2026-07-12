from __future__ import annotations

from fastapi.testclient import TestClient
from tamthuc_api.app import create_app


def test_not_found_envelope() -> None:
    c = TestClient(create_app())
    r = c.get("/api/v1/reports/missing")
    assert r.status_code == 404
    err = r.json()["error"]
    assert err["code"] == "NOT_FOUND"
    assert "request_id" in err


def test_not_implemented_timing() -> None:
    c = TestClient(create_app())
    r = c.post("/api/v1/timing/optimize")
    assert r.status_code == 501
    assert r.json()["error"]["code"] == "NOT_IMPLEMENTED"


def test_validation_error() -> None:
    c = TestClient(create_app())
    r = c.post("/api/v1/calculate/qimen", json={"longitude": 999})
    assert r.status_code == 422  # pydantic validation
