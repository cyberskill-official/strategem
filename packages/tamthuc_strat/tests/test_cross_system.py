"""FR-STRAT-004 cross-system validate tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from tamthuc_strat.cross_system import (
    CrossSystemRequest,
    stance_from_cach_cuc,
    validate,
)

FIX = Path(__file__).parent / "fixtures" / "cross_system_agreement.json"


def test_stance_pure() -> None:
    assert stance_from_cach_cuc([{"polarity": "cat"}, {"polarity": "cat"}]) == "favorable"
    assert stance_from_cach_cuc([{"polarity": "hung"}]) == "unfavorable"
    assert stance_from_cach_cuc([]) == "mixed"
    assert stance_from_cach_cuc([{"polarity": "cat"}, {"polarity": "hung"}]) == "mixed"


def test_agree_case_two_engines() -> None:
    data = json.loads(FIX.read_text(encoding="utf-8"))["agree_case"]
    calls: list[str] = []

    def eng(he: str, _body: dict[str, Any]) -> dict[str, Any]:
        calls.append(he)
        out: dict[str, Any] = dict(data[he])
        return out

    req = CrossSystemRequest(
        datetime=datetime(2004, 1, 1, 10, 30),
        systems=["ky_mon", "luc_nham"],
    )
    result = validate(req, {"ky_mon": eng, "luc_nham": eng})
    assert len(result.reads) == 2
    assert all(r.available for r in result.reads)
    assert calls.count("ky_mon") == 1
    assert calls.count("luc_nham") == 1
    assert "verdict" not in result.model_dump()
    assert result.reads[0].stance == "favorable"
    assert result.reads[1].stance == "favorable"
    assert result.agreement.agree is True


def test_different_scope_not_contradiction() -> None:
    data = json.loads(FIX.read_text(encoding="utf-8"))["divergent_scope_case"]

    def eng(he: str, _body: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = dict(data[he])
        return out

    req = CrossSystemRequest(
        datetime=datetime(2004, 1, 1, 10, 30),
        systems=["ky_mon", "thai_at"],
    )
    result = validate(req, {"ky_mon": eng, "thai_at": eng})
    labels = [x.get("label") for x in result.agreement.by_scope]
    assert "different-scope-not-contradiction" in labels
    assert len(result.reads) == 2


def test_unavailable_system() -> None:
    req = CrossSystemRequest(
        datetime=datetime(2004, 1, 1),
        systems=["ky_mon", "thai_at"],
    )
    result = validate(req, {"ky_mon": lambda h, b: {"cach_cuc": [], "cache_key": "x"}})
    assert any(not r.available for r in result.reads)


def test_determinism() -> None:
    def eng(he: str, _b: dict[str, Any]) -> dict[str, Any]:
        return {"cache_key": he, "cach_cuc": [{"polarity": "cat"}]}

    req = CrossSystemRequest(datetime=datetime(2004, 1, 1), systems=["ky_mon", "luc_nham"])
    a = validate(req, {"ky_mon": eng, "luc_nham": eng})
    b = validate(req, {"ky_mon": eng, "luc_nham": eng})
    assert a.model_dump() == b.model_dump()
