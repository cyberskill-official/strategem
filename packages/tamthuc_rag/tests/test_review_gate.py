from __future__ import annotations

from tamthuc_rag.review.gate import WITHHELD_SUMMARY, decide, process_interpretation
from tamthuc_rag.review.models import ReviewDecision
from tamthuc_rag.review.policy import LOW_CONFIDENCE_THRESHOLD, ReviewPolicy
from tamthuc_rag.review.queue import ReviewQueue
from tamthuc_rag.schema import AIDisclosure, Interpretation


def _interp(req: bool = True, conf: float = 0.2) -> Interpretation:
    return Interpretation(
        beginner="SECRET_PENDING_BEGINNER",
        expert="SECRET_PENDING_EXPERT",
        recommendations=[{"text": "SECRET_REC", "citations": ["c1"]}],
        citations=[],
        confidence=conf,
        requires_human_review=req,
        ai_disclosure=AIDisclosure(model="stub", prompt_version="1", retrieved_citation_ids=["c1"]),
    )


def test_not_required_released() -> None:
    q = ReviewQueue()
    out = process_interpretation(_interp(req=False, conf=0.9), q)
    assert out["released"] is True
    assert out["interpretation"]["review_status"] == "not_required"
    assert out["interpretation"]["beginner"] == "SECRET_PENDING_BEGINNER"


def test_low_confidence_withholds_text() -> None:
    """D-REVIEW-001: confidence < 0.55 must withhold beginner/expert (not soft-release)."""
    q = ReviewQueue()
    out = process_interpretation(_interp(req=False, conf=0.54), q, high_stakes=False)
    assert out["released"] is False
    view = out["withheld_view"]
    assert view["review_status"] == "pending"
    assert view["beginner"] == WITHHELD_SUMMARY
    assert view["expert"] == WITHHELD_SUMMARY
    assert "SECRET_PENDING" not in view["beginner"]
    assert "SECRET_PENDING" not in view["expert"]
    assert view["recommendations"] == []
    assert out["ticket"] is not None


def test_requires_flag_withholds_even_above_threshold() -> None:
    q = ReviewQueue()
    out = process_interpretation(_interp(req=True, conf=0.8), q, high_stakes=False)
    assert out["released"] is False
    assert "SECRET_PENDING" not in out["withheld_view"]["beginner"]


def test_high_stakes_withhold_and_decide() -> None:
    q = ReviewQueue()
    out = process_interpretation(_interp(req=True), q, high_stakes=True)
    assert out["released"] is False
    tid = out["ticket"]["ticket_id"]
    view = out["withheld_view"]
    assert view["review_status"] == "pending"
    assert view["beginner"] == WITHHELD_SUMMARY
    assert view["expert"] == WITHHELD_SUMMARY
    assert view["summary"] == WITHHELD_SUMMARY
    assert "SECRET_PENDING" not in str(view)
    with __import__("pytest").raises(PermissionError):
        decide(tid, ReviewDecision(decision="approve", reason="ok", reviewer="a", role="user"), q)
    with __import__("pytest").raises(ValueError):
        decide(
            tid,
            ReviewDecision(decision="approve", reason="  ", reviewer="r", role="reviewer"),
            q,
        )
    ok = decide(
        tid,
        ReviewDecision(decision="approve", reason="looks good", reviewer="r1", role="reviewer"),
        q,
    )
    assert ok["released"] is True
    assert ok["interpretation"]["review_status"] == "approved"
    assert ok["interpretation"]["beginner"] == "SECRET_PENDING_BEGINNER"
    assert q.audit and q.audit[0].reason == "looks good"


def test_policy_threshold_is_055() -> None:
    assert LOW_CONFIDENCE_THRESHOLD == 0.55
    pol = ReviewPolicy()
    assert pol.requires_review(_interp(req=False, conf=0.549)) is True
    assert pol.requires_review(_interp(req=False, conf=0.55)) is False
    assert pol.requires_review(_interp(req=False, conf=0.55), high_stakes=True) is True
