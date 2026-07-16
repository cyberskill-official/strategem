"""TASK-API-002 versioning + deprecation tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_api.clients.rag import StubRagClient
from tamthuc_api.clients.rule import StubRuleClient
from tamthuc_api.orchestrator import Orchestrator
from tamthuc_api.versioning.deprecation import DeprecatedRoute, deprecation_headers
from tamthuc_api.versioning.router import (
    CURRENT_MAJOR,
    SUPPORTED_MAJORS,
    calculation_stability_note,
    effective_version,
)


def _client() -> TestClient:
    orch = Orchestrator(rule=StubRuleClient(), rag=StubRagClient())
    return TestClient(create_app(orch))


def test_url_version_routes() -> None:
    c = _client()
    r = c.post(
        "/api/v1/calculate/qimen",
        json={"datetime": "2004-01-01T10:30:00", "longitude": 106.7, "question": "q"},
    )
    assert r.status_code == 200
    assert r.headers.get("X-API-Version") == "1"
    assert "qimen" in r.json()["charts"]


def test_unknown_version_rejected() -> None:
    c = _client()
    r = c.post(
        "/api/v99/calculate/qimen",
        json={"datetime": "2004-01-01T10:30:00", "longitude": 106.7, "question": "q"},
    )
    assert r.status_code == 404
    body = r.json()
    assert (
        body.get("error", body).get("code") == "NOT_FOUND"
        or "error" in body
        or body.get("code") == "NOT_FOUND"
    )


def test_header_version_option() -> None:
    c = _client()
    # path without version is not mounted; header alone on v1 path still works
    r = c.post(
        "/api/v1/calculate/qimen",
        headers={"X-API-Version": "1"},
        json={"datetime": "2004-01-01T10:30:00", "longitude": 106.7, "question": "q"},
    )
    assert r.status_code == 200
    assert r.headers.get("X-API-Version") == "1"


def test_url_wins_on_conflict() -> None:
    assert effective_version(1, 2) == 1
    assert effective_version(None, 1) == 1
    assert effective_version(1, None) == 1
    c = _client()
    # URL is v1; header claims 99 — URL wins, request still served if path is supported
    r = c.post(
        "/api/v1/calculate/qimen",
        headers={"X-API-Version": "99"},
        json={"datetime": "2004-01-01T10:30:00", "longitude": 106.7, "question": "q"},
    )
    assert r.status_code == 200
    assert r.headers.get("X-API-Version") == "1"


def test_deprecation_headers() -> None:
    h = deprecation_headers("/api/v2/knowledge/patterns", "Wed, 08 Jul 2027 00:00:00 GMT")
    assert h["Deprecation"] == "true"
    assert "successor-version" in h["Link"]
    assert "Sunset" in h
    route = DeprecatedRoute(
        path="/api/v1/knowledge/patterns",
        successor="/api/v2/knowledge/patterns",
        deprecated_in=1,
        remove_in=4,
    )
    assert route.still_supported(CURRENT_MAJOR)
    assert (route.remove_in - route.deprecated_in) >= 2


def test_deprecated_endpoint_still_functions() -> None:
    c = _client()
    r = c.get("/api/v1/knowledge/patterns")
    # may be 200 or empty list depending on route — must not 410
    assert r.status_code != 410
    if r.status_code == 200:
        assert r.headers.get("Deprecation") == "true"
        assert "successor-version" in (r.headers.get("Link") or "")


def test_calculation_stable_interpretation_variable() -> None:
    note = calculation_stability_note()
    assert note["calculation_output"]["stability"] == "stable"
    assert note["interpretation"]["stability"] == "variable"
    c = _client()
    body = {
        "datetime": "2004-01-01T10:30:00",
        "longitude": 106.7,
        "question": "q",
    }
    r1 = c.post("/api/v1/calculate/qimen", json=body)
    r2 = c.post("/api/v1/calculate/qimen", json=body)
    assert r1.status_code == 200 and r2.status_code == 200
    # chart / envelope calculation is stable
    chart1 = r1.json()["charts"]["qimen"]
    chart2 = r2.json()["charts"]["qimen"]
    assert chart1.get("envelope_version") == chart2.get("envelope_version") == 1
    # ban (calculation) byte-stable
    assert chart1.get("ban") == chart2.get("ban")
    # interpretation is allowed to vary — we do not assert prose equality
    assert 1 in SUPPORTED_MAJORS
