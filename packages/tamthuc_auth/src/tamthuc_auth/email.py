"""Email dispatch seam — FR-AUTH-003 (provider-agnostic; fake for tests)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class EmailSender(Protocol):
    def send(self, template: str, to: str, context: dict[str, Any]) -> None: ...


@dataclass
class FakeEmailSender:
    """In-memory sink for tests; never hits a network."""

    sent: list[dict[str, Any]] = field(default_factory=list)

    def send(self, template: str, to: str, context: dict[str, Any]) -> None:
        # never log the raw token field if present — tests assert this
        safe = {k: v for k, v in context.items() if k != "token"}
        self.sent.append({"template": template, "to": to, "context": safe, "_raw": context})


_default: FakeEmailSender = FakeEmailSender()


def get_email_sender() -> EmailSender:
    return _default


def reset_email_sender() -> FakeEmailSender:
    global _default
    _default = FakeEmailSender()
    return _default
