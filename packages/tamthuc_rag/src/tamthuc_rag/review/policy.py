from __future__ import annotations

from tamthuc_rag.schema import Interpretation


class ReviewPolicy:
    """Drives requires_human_review agreement with the queue."""

    low_confidence: float = 0.5

    def requires_review(self, interp: Interpretation, *, high_stakes: bool = False) -> bool:
        if high_stakes:
            return True
        if interp.confidence < self.low_confidence:
            return True
        return bool(interp.requires_human_review)
