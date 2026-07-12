"""FR-KB-004 curation workflow tests."""

from __future__ import annotations

import pytest
from tamthuc_kb.curation.models import ReviewObjectType
from tamthuc_kb.curation.queue import CurationQueue
from tamthuc_kb.curation.release_gate import release_gate
from tamthuc_kb.curation.review import CurationError, decide


def test_submit_accept_versioning() -> None:
    q = CurationQueue()
    item = q.submit(
        ReviewObjectType.pattern,
        "qimen_thanh_long_hoi_dau",
        2,
        {"polarity": "cat"},
        by="author1",
    )
    assert item.state.value == "in_review"
    d = decide(q, item.id, reviewer_id="master1", decision="accept", reason="classical match")
    assert d.result_version == 2
    assert q.get(item.id) is not None
    assert q.get(item.id).state.value == "accepted"  # type: ignore[union-attr]


def test_reject_requires_reason() -> None:
    q = CurationQueue()
    item = q.submit(ReviewObjectType.classical_unit, "u1", 1, {}, by="a")
    with pytest.raises(CurationError):
        decide(q, item.id, reviewer_id="m", decision="reject", reason="")
    d = decide(q, item.id, reviewer_id="m", decision="reject", reason="wrong translation")
    assert d.decision == "reject"
    assert d.result_version is None


def test_cannot_self_review() -> None:
    q = CurationQueue()
    item = q.submit(ReviewObjectType.pattern, "p1", 1, {}, by="same")
    with pytest.raises(CurationError):
        decide(q, item.id, reviewer_id="same", decision="accept", reason="ok")


def test_release_gate_unsigned() -> None:
    q = CurationQueue()
    item = q.submit(ReviewObjectType.pattern, "p1", 3, {}, by="a")
    # not accepted yet
    gate = release_gate(
        "2026.07",
        queue=q,
        active_objects={("pattern", "p1"): 3},
        last_release_versions={("pattern", "p1"): 2},
    )
    assert gate.passed is False
    assert gate.unsigned
    decide(q, item.id, reviewer_id="m", decision="accept", reason="ok")
    gate2 = release_gate(
        "2026.07",
        queue=q,
        active_objects={("pattern", "p1"): 3},
        last_release_versions={("pattern", "p1"): 2},
    )
    assert gate2.passed is True
