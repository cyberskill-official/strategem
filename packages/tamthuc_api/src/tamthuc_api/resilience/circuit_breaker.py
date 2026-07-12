from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TypeVar

T = TypeVar("T")


class CircuitState(StrEnum):
    closed = "closed"
    open = "open"
    half_open = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    cooldown_seconds: float = 30.0
    failures: int = 0
    state: CircuitState = CircuitState.closed
    opened_at: float | None = None
    transitions: list[str] = field(default_factory=list)

    def _transition(self, new: CircuitState) -> None:
        if new != self.state:
            self.transitions.append(f"{self.state}->{new}")
            self.state = new
            if new == CircuitState.open:
                self.opened_at = time.monotonic()

    def before_call(self) -> None:
        if self.state == CircuitState.open:
            assert self.opened_at is not None
            if time.monotonic() - self.opened_at >= self.cooldown_seconds:
                self._transition(CircuitState.half_open)
            else:
                raise RuntimeError("circuit_open")

    def record_success(self) -> None:
        self.failures = 0
        self._transition(CircuitState.closed)

    def record_failure(self) -> None:
        self.failures += 1
        if self.state == CircuitState.half_open or self.failures >= self.failure_threshold:
            self._transition(CircuitState.open)

    def call(self, fn: Callable[[], T]) -> T:
        self.before_call()
        try:
            result = fn()
        except Exception:
            self.record_failure()
            raise
        self.record_success()
        return result
