from __future__ import annotations

import pytest
from tamthuc_api.resilience.errors import map_upstream_error
from tamthuc_api.resilience.retry import PermanentError, TransientError, retry_call


def test_retry_transient_then_success() -> None:
    n = {"i": 0}

    def flaky() -> str:
        n["i"] += 1
        if n["i"] < 3:
            raise TransientError("temp")
        return "done"

    assert retry_call(flaky, max_attempts=5, base_delay=0.0, sleep=lambda _d: None) == "done"
    assert n["i"] == 3


def test_no_retry_permanent() -> None:
    with pytest.raises(PermanentError):
        retry_call(lambda: (_ for _ in ()).throw(PermanentError("400")), max_attempts=5)


def test_map_upstream_status() -> None:
    e = map_upstream_error(RuntimeError("circuit_open"))
    assert e.http_status == 503
    assert e.code.startswith("UPSTREAM_")
    e2 = map_upstream_error(RuntimeError("other"))
    assert e2.http_status == 502
