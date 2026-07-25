"""COV-008 scenario compare + COV-012 cross-system validate API."""

from __future__ import annotations

from auth_helpers import auth_header, register_and_login
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app


def test_scenario_compare_returns_ranked() -> None:
    client = TestClient(create_app())
    tokens = register_and_login(client, email="scenario@example.com", tier="premium")
    r = client.post(
        "/api/v1/scenario/compare",
        headers=auth_header(tokens["access"]),
        json={
            "top_n": 2,
            "scenarios": [
                {
                    "label": "sáng",
                    "start": "2004-01-01T08:00:00",
                    "end": "2004-01-01T12:00:00",
                    "granularity": "gio",
                },
                {
                    "label": "chiều",
                    "start": "2004-01-01T14:00:00",
                    "end": "2004-01-01T18:00:00",
                    "granularity": "gio",
                },
            ],
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["results"]) == 2
    assert set(body["ranked_labels"]) == {"sáng", "chiều"}
    assert body.get("disclaimer")
    assert body.get("ai_disclosure", {}).get("used_llm") is False


def test_scenario_compare_rejects_one() -> None:
    client = TestClient(create_app())
    tokens = register_and_login(client, email="scenario2@example.com", tier="premium")
    r = client.post(
        "/api/v1/scenario/compare",
        headers=auth_header(tokens["access"]),
        json={
            "scenarios": [
                {
                    "label": "only",
                    "start": "2004-01-01T08:00:00",
                    "end": "2004-01-01T10:00:00",
                }
            ]
        },
    )
    assert r.status_code == 400


def test_cross_system_validate_three_columns() -> None:
    client = TestClient(create_app())
    tokens = register_and_login(client, email="cross@example.com", tier="premium")
    r = client.post(
        "/api/v1/cross-system/validate",
        headers=auth_header(tokens["access"]),
        json={
            "datetime": "2004-01-01T10:30:00",
            "tz": "+07:00",
            "longitude": 106.7,
            "systems": ["qimen", "liuren", "taiyi"],
            "loai_cau_hoi": "trach_thoi",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    reads = body.get("reads") or []
    assert len(reads) >= 2
    for rd in reads:
        if rd.get("available"):
            assert rd.get("he")
            assert rd.get("stance") in {"favorable", "mixed", "unfavorable"}
            # no invented score field
            assert "merged_score" not in rd
    assert body.get("agreement")
    assert body.get("disclaimer")
