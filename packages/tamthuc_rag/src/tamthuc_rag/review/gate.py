from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from tamthuc_rag.review.models import AuditRow, ReviewDecision, ReviewTicket
from tamthuc_rag.review.policy import ReviewPolicy
from tamthuc_rag.review.queue import ReviewQueue
from tamthuc_rag.schema import Interpretation


def process_interpretation(
    interp: Interpretation,
    queue: ReviewQueue,
    *,
    policy: ReviewPolicy | None = None,
    high_stakes: bool = False,
) -> dict[str, Any]:
    """Gate interpretation release.

    - No review needed → release with review_status=not_required.
    - Soft review (low conf / flag, not high-stakes) → still release beginner/expert
      text so product/e2e surfaces stay stable; enqueue a pending ticket.
    - High-stakes (medical/legal/financial) → hard withhold full reading; withheld_view
      keeps a stable shape including beginner/expert placeholders + summary.
    """
    pol = policy or ReviewPolicy()
    needs = pol.requires_review(interp, high_stakes=high_stakes)
    if not needs:
        disc = interp.ai_disclosure.model_copy(update={"limits": interp.ai_disclosure.limits})
        # attach review_status via dict view
        out = interp.model_dump()
        out["review_status"] = "not_required"
        out["ai_disclosure"] = disc.model_dump()
        return {"released": True, "interpretation": out, "ticket": None}

    ticket = queue.enqueue(ReviewTicket(interpretation=interp, review_status="pending"))

    # Soft path: educational / low-confidence — show the reading, flag pending review.
    if not high_stakes:
        out = interp.model_dump()
        out["review_status"] = "pending"
        out["human_review_gate"] = "pending"
        out["ai_disclosure"] = {
            **interp.ai_disclosure.model_dump(),
            "review_status": "pending",
        }
        return {"released": True, "interpretation": out, "ticket": ticket.model_dump()}

    # High-stakes: withhold free-form claims; keep API keys stable for clients/tests.
    summary = "This interpretation is under human review."
    withheld = {
        "review_status": "pending",
        "summary": summary,
        "beginner": summary,
        "expert": summary,
        "recommendations": [],
        "citations": [c.model_dump() for c in interp.citations],
        "confidence": float(interp.confidence),
        "requires_human_review": True,
        "ai_disclosure": {
            **interp.ai_disclosure.model_dump(),
            "review_status": "pending",
        },
    }
    return {"released": False, "withheld_view": withheld, "ticket": ticket.model_dump()}


def decide(
    ticket_id: str,
    decision: ReviewDecision,
    queue: ReviewQueue,
) -> dict[str, Any]:
    if decision.role != "reviewer":
        raise PermissionError("reviewer role required")
    if not decision.reason.strip():
        raise ValueError("reason required")
    ticket = queue.get(ticket_id)
    if ticket is None:
        raise KeyError(ticket_id)
    if decision.decision == "approve":
        ticket.review_status = "approved"
        released = ticket.interpretation.model_dump()
        released["review_status"] = "approved"
        result = {"released": True, "interpretation": released}
    else:
        ticket.review_status = "rejected"
        result = {
            "released": False,
            "withheld_view": {
                "review_status": "rejected",
                "summary": "Interpretation not released.",
            },
        }
    ticket.reason = decision.reason
    ticket.reviewer = decision.reviewer
    queue.audit.append(
        AuditRow(
            ticket_id=ticket_id,
            reviewer=decision.reviewer,
            decision=decision.decision,
            reason=decision.reason,
            timestamp=datetime.now(UTC).isoformat(),
        )
    )
    return result
