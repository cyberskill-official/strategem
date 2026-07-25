from __future__ import annotations

import pytest
from tamthuc_api.persistence import PersistenceService


def test_single_system_persist() -> None:
    svc = PersistenceService()
    env = {"envelope_version": 1, "he": "ky_mon", "ban": {"x": 1}}
    res = svc.persist_query_result(
        "user-1",
        {"datetime": "2004-01-01T10:30:00", "question_type": "trach_thoi"},
        {"qimen": env},
        patterns=[{"id": "p1"}],
    )
    assert res.query_id
    assert len(res.chart_ids) == 1
    row = svc.charts.get(res.chart_ids[0])
    assert row is not None
    assert row["chart_data"] is env  # verbatim reference
    assert row["query_id"] == res.query_id
    assert len(svc.queries.rows) == 1  # type: ignore[attr-defined]


def test_multi_system_shared_query_id() -> None:
    svc = PersistenceService()
    charts = {
        "qimen": {"envelope_version": 1, "he": "ky_mon"},
        "liuren": {"envelope_version": 1, "he": "luc_nham"},
        "taiyi": {"envelope_version": 1, "he": "thai_at"},
    }
    res = svc.persist_query_result("u", {"datetime": "t"}, charts, [])
    assert len(res.chart_ids) == 3
    qids = {svc.charts.get(c)["query_id"] for c in res.chart_ids}  # type: ignore[index]
    assert qids == {res.query_id}


def test_transactional_failure() -> None:
    svc = PersistenceService(fail_next=True)
    with pytest.raises(RuntimeError):
        svc.persist_query_result("u", {}, {"qimen": {}}, [])
    assert svc.queries.rows == []  # type: ignore[attr-defined]
    assert svc.charts.rows == []  # type: ignore[attr-defined]


def test_report_rls() -> None:
    svc = PersistenceService()
    res = svc.persist_query_result(
        "owner",
        {},
        {"qimen": {"envelope_version": 1}},
        [],
        report={"summary": "ok"},
    )
    assert res.report_id
    assert svc.reports.get(res.report_id, "owner") is not None
    assert svc.reports.get(res.report_id, "other") is None


def test_get_report_by_query_id() -> None:
    svc = PersistenceService()
    report = {
        "report_id": "rep-abc",
        "query_id": "will-be-overwritten",
        "chart_summary": {"he": "ky_mon", "dau_vao": {}, "lich_phap_summary": "x"},
        "detected_patterns": [],
        "interpretation": {"beginner": "b", "expert": "e", "recommendations": []},
        "citations": [{"source": "s", "locator": "l"}],
        "confidence": 0.5,
        "ai_disclosure": {"model": "m", "limits": "l", "review_status": "not_required"},
        "created_at": "2004-01-01T00:00:00Z",
    }
    res = svc.persist_query_result(
        "u",
        {},
        {"qimen": {"envelope_version": 1}},
        [],
        report=report,
        full_result={"report": report, "report_id": "rep-abc"},
    )
    by_rid = svc.get_report(res.report_id or "")
    assert by_rid is not None
    by_qid = svc.get_report(res.query_id)
    assert by_qid is not None
    assert by_qid.get("report_id") == res.report_id
    assert by_qid.get("query_id") == res.query_id
