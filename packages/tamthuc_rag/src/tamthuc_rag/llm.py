from __future__ import annotations

from typing import Any, Protocol


class LlmClient(Protocol):
    model: str

    def complete(self, prompt: str) -> dict[str, Any]: ...


class StubLlm:
    """Deterministic stub for CI — no network."""

    model = "stub-llm"

    def complete(self, prompt: str) -> dict[str, Any]:
        # Extract first citation id if present
        cites: list[str] = []
        for line in prompt.splitlines():
            if line.startswith("- ") and ":" in line:
                cites.append(line[2:].split(":", 1)[0].strip())
        return {
            "beginner": "A cautious educational reading of the chart patterns.",
            "expert": "Technical notes grounded in the retrieved classical units.",
            "recommendations": [
                {
                    "text": "Reflect on timing using the cited classical guidance.",
                    "citations": cites[:1] or [],
                }
            ],
        }
