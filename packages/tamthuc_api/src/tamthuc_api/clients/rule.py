"""Pattern match client — TASK-API-001."""

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


class LocalRuleClient:
    """Read cach_cuc from the engine envelope; never re-detects patterns."""

    def __init__(self) -> None:
        self.last_envelope: dict[str, Any] | None = None

    def match(self, envelope: dict[str, Any]) -> list[dict[str, Any]]:
        self.last_envelope = envelope
        raw = envelope.get("cach_cuc")
        if isinstance(raw, list) and raw:
            out: list[dict[str, Any]] = []
            for item in raw:
                if isinstance(item, dict):
                    out.append(
                        {
                            "id": item.get("id") or "pattern",
                            "name": item.get("name") or item.get("id") or "pattern",
                            "cung": item.get("cung"),
                            "polarity": item.get("polarity") or "trung",
                            "score": item.get("score"),
                            "citations": list(item.get("citations") or []),
                        }
                    )
            return out
        return []
