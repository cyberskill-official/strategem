from __future__ import annotations

from tamthuc_rag.review.gate import decide, process_interpretation
from tamthuc_rag.review.models import ReviewDecision
from tamthuc_rag.review.queue import ReviewQueue
from tamthuc_rag.schema import AIDisclosure, Interpretation


def _interp(req: bool = True, conf: float = 0.2) -> Interpretation:
    return Interpretation(
        beginner="b",
        expert="e",
        recommendations=[{"text": "t", "citations": ["c1"]}],
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


def test_pending_withhold_and_decide() -> None:
    q = ReviewQueue()
    out = process_interpretation(_interp(req=True), q)
    assert out["released"] is False
    tid = out["ticket"]["ticket_id"]
    assert out["withheld_view"]["review_status"] == "pending"
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
    assert q.audit and q.audit[0].reason == "looks good"
