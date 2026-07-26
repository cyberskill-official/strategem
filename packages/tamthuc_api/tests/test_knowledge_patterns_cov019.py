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
    """TASK-API-001 / TASK-API-005: GET /knowledge/patterns?system= must filter (not return all)."""
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
    # liuren filter must not include qimen / taiyi
    lr = client.get("/api/v1/knowledge/patterns?system=liuren&limit=500")
    assert lr.status_code == 200
    lr_rows = lr.json()["patterns"]
    assert lr_rows
    assert all(str(p.get("system")) == "liuren" for p in lr_rows)
    assert all(str(p.get("system")) not in {"qimen", "taiyi"} for p in lr_rows)
    assert lr.json()["total"] < all_total


def test_system_alias_ky_mon_matches_qimen() -> None:
    """TASK-API-005: Vietnamese he codes and he= alias match canonical system=qimen."""
    client = TestClient(create_app())
    by_system = client.get("/api/v1/knowledge/patterns?system=qimen&limit=500")
    by_alias = client.get("/api/v1/knowledge/patterns?system=ky_mon&limit=500")
    by_he = client.get("/api/v1/knowledge/patterns?he=qimen&limit=500")
    assert by_system.status_code == 200
    assert by_alias.status_code == 200
    assert by_he.status_code == 200
    t_system = by_system.json()["total"]
    t_alias = by_alias.json()["total"]
    t_he = by_he.json()["total"]
    assert t_system > 0
    assert t_alias == t_system
    assert t_he == t_system
    for body in (by_system.json(), by_alias.json(), by_he.json()):
        assert all(str(p.get("system")) == "qimen" for p in body["patterns"])


def test_unknown_system_returns_empty() -> None:
    """TASK-API-005: unknown system/he MUST return empty 200, not the full catalog."""
    client = TestClient(create_app())
    all_r = client.get("/api/v1/knowledge/patterns?limit=500")
    assert all_r.status_code == 200
    assert all_r.json()["total"] > 0
    r = client.get("/api/v1/knowledge/patterns?system=nope&limit=500")
    assert r.status_code == 200
    body = r.json()
    assert body["patterns"] == []
    assert body["total"] == 0
    r_he = client.get("/api/v1/knowledge/patterns?he=nope&limit=500")
    assert r_he.status_code == 200
    assert r_he.json()["patterns"] == []
    assert r_he.json()["total"] == 0
