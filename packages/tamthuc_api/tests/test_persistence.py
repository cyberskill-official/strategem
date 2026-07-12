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
    assert len(svc.queries.rows) == 1


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
    assert svc.queries.rows == []
    assert svc.charts.rows == []


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
