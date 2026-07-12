from __future__ import annotations

import pytest
from tamthuc_api.resilience.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_transitions() -> None:
    cb = CircuitBreaker(failure_threshold=2, cooldown_seconds=0.0)

    def boom() -> None:
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        cb.call(boom)
    with pytest.raises(RuntimeError):
        cb.call(boom)
    assert cb.state == CircuitState.open

    # cooldown 0 → half-open on next before_call
    def ok() -> str:
        return "ok"

    assert cb.call(ok) == "ok"
    assert cb.state.value == "closed"
    assert any("open" in t for t in cb.transitions)
