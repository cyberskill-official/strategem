"""Accept/reject decisions — FR-KB-004."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from tamthuc_kb.curation.models import ReviewDecision, ReviewState
from tamthuc_kb.curation.queue import CurationQueue


class CurationError(ValueError):
    pass


def decide(
    queue: CurationQueue,
    item_id: str,
    *,
    reviewer_id: str,
    decision: Literal["accept", "reject"],
    reason: str,
    master_role: bool = True,
) -> ReviewDecision:
    if not master_role:
        raise CurationError("reviewer must hold master/expert role")
    if not reason or not reason.strip():
        raise CurationError("reason required")
    item = queue.get(item_id)
    if item is None:
        raise CurationError("item not found")
    if item.state != ReviewState.in_review:
        raise CurationError("item not in_review")
    if item.submitted_by == reviewer_id:
        raise CurationError("reviewer cannot decide own submission")

    result_version: int | None = None
    if decision == "accept":
        result_version = item.object_version  # monotonic: accepted at this version
        new_state = ReviewState.accepted
    else:
        new_state = ReviewState.rejected

    updated = item.model_copy(update={"state": new_state})
    queue.update(updated)

    return ReviewDecision(
        item_id=item.id,
        object_type=item.object_type,
        object_id=item.object_id,
        reviewer_id=reviewer_id,
        decision=decision,
        reason=reason.strip(),
        decided_at=datetime.now(UTC),
        result_version=result_version,
    )
