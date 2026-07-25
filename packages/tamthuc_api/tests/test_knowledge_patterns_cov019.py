"""COV-019: knowledge patterns API from KB seed (≥150)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tamthuc_api.app import create_app


def test_list_patterns_seeded() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/knowledge/patterns?limit=500")
    assert r.status_code == 200, r.text
    body = r.json()
    patterns = body["patterns"]
    assert body["total"] >= 150 or len(patterns) >= 150
    assert patterns
    p0 = patterns[0]
    assert p0.get("name") or p0.get("name_han")
    assert p0.get("system") in {"qimen", "liuren", "taiyi"} or p0.get("he")


def test_filter_by_he_and_search() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/knowledge/patterns?he=qimen&limit=50")
    assert r.status_code == 200
    rows = r.json()["patterns"]
    assert all(str(p.get("system")) == "qimen" for p in rows)
    # no prophecy keywords in modern gloss
    blob = " ".join(str(p.get("meaning_modern") or "") for p in rows).lower()
    assert "guaranteed fate" not in blob


def test_filter_by_system_query_param() -> None:
    """TASK-API-001: GET /knowledge/patterns?system= must filter (not return all)."""
    client = TestClient(create_app())
    all_r = client.get("/api/v1/knowledge/patterns?limit=500")
    assert all_r.status_code == 200
    all_total = all_r.json()["total"]
    r = client.get("/api/v1/knowledge/patterns?system=qimen&limit=500")
    assert r.status_code == 200
    body = r.json()
    rows = body["patterns"]
    assert body["total"] < all_total
    assert rows
    assert all(str(p.get("system")) == "qimen" for p in rows)
    # liuren filter must not include qimen
    lr = client.get("/api/v1/knowledge/patterns?system=liuren&limit=500")
    assert lr.status_code == 200
    lr_rows = lr.json()["patterns"]
    assert lr_rows
    assert all(str(p.get("system")) == "liuren" for p in lr_rows)
    assert lr.json()["total"] < all_total
