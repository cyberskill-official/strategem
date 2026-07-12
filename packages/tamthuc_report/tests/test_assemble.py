from __future__ import annotations

from uuid import uuid4

import pytest

from tamthuc_report.assemble import AssembleError, assemble


def _env() -> dict:
    return {
        "he": "ky_mon",
        "dau_vao": {"datetime": "2004-01-01T10:30:00"},
        "lich_phap": {"summary": "甲子日"},
        "cach_cuc": [{"id": "c1", "name": "Cach 1", "polarity": "cat"}],
        "ban": {"x": 1},
    }


def _interp() -> dict:
    return {
        "beginner": "Good day",
        "expert": "Detailed",
        "confidence": 0.81,
        "citations": [{"source": "Book", "locator": "1.1"}],
        "ai_disclosure": {
            "model": "stub",
            "limits": "not advice",
            "review_status": "not_required",
        },
        "recommendations": ["wait"],
    }


def test_copy_equality() -> None:
    env = _env()
    before = dict(env)
    qid = uuid4()
    r = assemble(env, _interp(), qid)
    assert r.chart_summary.he == "ky_mon"
    assert r.chart_summary.dau_vao == before["dau_vao"]
    assert r.detected_patterns[0].id == "c1"
    assert r.confidence == 0.81
    assert r.ai_disclosure.model == "stub"
    assert env == before  # read-only


def test_missing_citation_rejected() -> None:
    with pytest.raises(AssembleError):
        assemble(_env(), {**_interp(), "citations": []}, uuid4())


def test_missing_disclosure_rejected() -> None:
    with pytest.raises(AssembleError):
        assemble(_env(), {**_interp(), "ai_disclosure": {}}, uuid4())
