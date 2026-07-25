"""COV-007: /api/v1/timing/optimize returns ranked windows (not 501)."""

from __future__ import annotations

from auth_helpers import auth_header, register_and_login
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app


def test_timing_optimize_returns_windows() -> None:
    client = TestClient(create_app())
    tokens = register_and_login(client, email="timing-ok@example.com", tier="premium")
    r = client.post(
        "/api/v1/timing/optimize",
        headers=auth_header(tokens["access"]),
        json={
            "start": "2004-01-01T08:00:00",
            "end": "2004-01-01T18:00:00",
            "granularity": "gio",
            "loai_cau_hoi": "trach_thoi",
            "tz": "+07:00",
            "longitude": 106.7,
            "top_n": 3,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "windows" in body
    assert 1 <= len(body["windows"]) <= 3
    w0 = body["windows"][0]
    assert "score" in w0
    assert "cast_ref" in w0
    assert "reasons" in w0
    assert body.get("disclaimer")
    assert body.get("ai_disclosure", {}).get("used_llm") is False
    # ranked descending
    scores = [w["score"] for w in body["windows"]]
    assert scores == sorted(scores, reverse=True)


def test_timing_optimize_rejects_inverted_range() -> None:
    client = TestClient(create_app())
    tokens = register_and_login(client, email="timing-bad@example.com", tier="premium")
    r = client.post(
        "/api/v1/timing/optimize",
        headers=auth_header(tokens["access"]),
        json={
            "start": "2004-01-02T00:00:00",
            "end": "2004-01-01T00:00:00",
            "top_n": 2,
        },
    )
    assert r.status_code == 400
