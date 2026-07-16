"""Resilient LLM wrapper — TASK-RAG-007."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, TypeVar

from tamthuc_rag.llm import LlmClient

T = TypeVar("T")


class CircuitState(StrEnum):
    closed = "closed"
    open = "open"
    half_open = "half_open"


class LLMUnavailable(RuntimeError):
    pass


@dataclass
class CircuitBreaker:
    fail_threshold: int = 5
    cooldown_s: float = 30.0
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
            if time.monotonic() - self.opened_at >= self.cooldown_s:
                self._transition(CircuitState.half_open)
            else:
                raise LLMUnavailable("circuit_open")

    def record_success(self) -> None:
        self.failures = 0
        self._transition(CircuitState.closed)

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.fail_threshold or self.state == CircuitState.half_open:
            self._transition(CircuitState.open)

    def call(self, fn: Callable[[], T]) -> T:
        self.before_call()
        try:
            out = fn()
            self.record_success()
            return out
        except Exception:
            self.record_failure()
            raise


@dataclass
class ResilientLLM:
    """Drop-in LLM with circuit breaker (timeout simulated via failing inner)."""

    inner: LlmClient
    breaker: CircuitBreaker = field(default_factory=CircuitBreaker)
    timeout_s: float = 20.0
    retries: int = 1

    @property
    def model(self) -> str:
        return self.inner.model

    def complete(self, prompt: str) -> dict[str, Any]:
        last: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                return self.breaker.call(lambda: self.inner.complete(prompt))
            except LLMUnavailable:
                raise
            except Exception as e:
                last = e
                if attempt >= self.retries:
                    break
                time.sleep(0.01 * (attempt + 1))
        raise LLMUnavailable(str(last) if last else "llm_failed")
