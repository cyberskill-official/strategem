"""COV-014 grade · COV-015 library · COV-016 onboarding API."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tamthuc_api.app import create_app


def test_practice_grade_cell_diffs() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/edu/practice/grade",
        json={
            "system": "qimen",
            "student_seat_ids": ["a", "wrong"],
            "engine_envelope": {
                "cach_cuc": [
                    {"id": "a", "name": "A"},
                    {"id": "b", "name": "B"},
                ]
            },
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["graded_slice"] == "cach_cuc_ids_only"
    assert any(d["kind"] == "missing" for d in body["cell_diffs"])
    assert any(d["kind"] == "extra" for d in body["cell_diffs"])
    assert "interpretation" not in body["graded_slice"]


def test_library_three_layers() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/edu/library")
    assert r.status_code == 200, r.text
    entries = r.json()["entries"]
    assert entries
    e0 = entries[0]
    assert e0.get("han") or e0.get("layers", {}).get("han")
    assert "layers" in e0
    assert set(e0["layers"].keys()) >= {"han", "bach_thoai", "dich"}


def test_onboarding_and_help() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/edu/onboarding")
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["steps"]) >= 3
    assert any(
        "AIDisclosure" in s.get("body", "") or "AI" in s.get("body", "") for s in body["steps"]
    )
    assert any(
        "HumanReview" in s.get("body", "") or "duyệt" in s.get("body", "") for s in body["steps"]
    )
    assert body["help"]
