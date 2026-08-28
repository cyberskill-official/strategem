from __future__ import annotations

from tamthuc_rag.schema import Interpretation

# Product rule (RAG-001 / D-REVIEW-001): confidence below this threshold is withheld.
LOW_CONFIDENCE_THRESHOLD = 0.55


class ReviewPolicy:
    """Drives requires_human_review agreement with the queue."""

    low_confidence: float = LOW_CONFIDENCE_THRESHOLD

    def requires_review(self, interp: Interpretation, *, high_stakes: bool = False) -> bool:
        if high_stakes:
            return True
        if interp.confidence < self.low_confidence:
            return True
        return bool(interp.requires_human_review)
