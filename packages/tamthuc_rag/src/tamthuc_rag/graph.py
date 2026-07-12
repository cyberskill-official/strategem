from __future__ import annotations

from typing import Protocol


class GraphRetriever(Protocol):
    def retrieve(
        self, query: str, *, system: str | None, k: int
    ) -> list[tuple[str, float, dict[str, str]]]:
        """Return (unit_id, score, layers)."""
        ...


class NullGraphRetriever:
    def retrieve(
        self, query: str, *, system: str | None, k: int
    ) -> list[tuple[str, float, dict[str, str]]]:
        return []


class StubGraphRetriever:
    """Returns fixed unit hits for tests."""

    def __init__(self, hits: list[tuple[str, float, dict[str, str]]] | None = None) -> None:
        self.hits = hits or []

    def retrieve(
        self, query: str, *, system: str | None, k: int
    ) -> list[tuple[str, float, dict[str, str]]]:
        out = self.hits
        if system and system != "all":
            # filter by embedded system tag in unit_id prefix if present
            out = [h for h in out if system in h[0] or True]
        return out[:k]
