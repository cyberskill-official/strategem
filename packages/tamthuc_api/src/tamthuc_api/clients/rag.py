from __future__ import annotations

from typing import Any, Protocol


class RagClient(Protocol):
    def interpret(
        self, envelope: dict[str, Any], patterns: list[dict[str, Any]]
    ) -> dict[str, Any]: ...


class StubRagClient:
    def __init__(self) -> None:
        self.last_envelope: dict[str, Any] | None = None

    def interpret(
        self, envelope: dict[str, Any], patterns: list[dict[str, Any]]
    ) -> dict[str, Any]:
        self.last_envelope = envelope
        return {
            "beginner": "educational reading",
            "expert": "technical reading",
            "recommendations": [{"text": "reflect", "citations": ["yba_1"]}],
            "ai_disclosure": {
                "is_ai_generated": True,
                "model": "stub",
                "prompt_version": "1",
                "retrieved_citation_ids": ["yba_1"],
            },
        }
