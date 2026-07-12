"""Optional advisory judge — FR-RAG-006 (marker-gated, never hard gate)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Judge(Protocol):
    version: str

    def entails(self, claim: str, passage: str) -> float:
        """Return entailment score in [0, 1]."""
        ...


class StubJudge:
    """Deterministic stub for CI; reports a fixed advisory band."""

    def __init__(self, score: float = 0.9, version: str = "stub-judge@1") -> None:
        self.version = version
        self._score = score

    def entails(self, claim: str, passage: str) -> float:
        if not claim.strip() or not passage.strip():
            return 0.0
        # crude token overlap for reproducibility
        ct = set(claim.lower().split())
        pt = set(passage.lower().split())
        if not ct:
            return 0.0
        overlap = len(ct & pt) / len(ct)
        return min(1.0, max(self._score * 0.5, overlap))
