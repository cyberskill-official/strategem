from __future__ import annotations

from typing import Any, Protocol


class RuleClient(Protocol):
    def match(self, envelope: dict[str, Any]) -> list[dict[str, Any]]: ...


class StubRuleClient:
    def __init__(self) -> None:
        self.last_envelope: dict[str, Any] | None = None

    def match(self, envelope: dict[str, Any]) -> list[dict[str, Any]]:
        self.last_envelope = envelope
        return [{"id": "stub_pattern", "score": 0.5, "citations": ["yba_1"]}]
