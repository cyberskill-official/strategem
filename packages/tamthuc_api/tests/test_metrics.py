from __future__ import annotations

from tamthuc_api.observability.analytics import track
from tamthuc_api.observability.logging import redact, structured_log
from tamthuc_api.observability.metrics import MetricsRegistry, p95, render_prometheus
from tamthuc_api.observability.sentry import capture_exception


def test_prometheus_families() -> None:
    reg = MetricsRegistry()
    reg.record_chart_gen(0.2, request_id="r1")
    reg.record_chart_gen(6.0, request_id="r1")
    reg.record_error()
    text = render_prometheus(reg)
    assert "chart_gen" in text
    assert 'family="business"' in text or "family=" in text
    assert "expert_validation_pass_ratio" in text
    assert "http_errors_total" in text


def test_alert_thresholds_synthetic() -> None:
    # chart p95 > 5s
    samples = [0.1] * 10 + [6.0] * 10
    assert p95(samples) > 5.0
    # error rate > 1%
    errors, total = 2, 100
    assert errors / total > 0.01


def test_request_id_correlation_and_redaction() -> None:
    rid = "req-abc"
    log_line = structured_log(
        "chart.cast",
        request_id=rid,
        birth_data={"date": "1990-01-01"},
        question="Will I get the job?",
    )
    assert rid in log_line
    assert "1990-01-01" not in log_line
    assert "Will I get the job" not in log_line
    assert "[REDACTED]" in log_line

    sentry = capture_exception(RuntimeError("boom"), request_id=rid, extra={"birth_data": "x"})
    assert sentry["request_id"] == rid
    assert sentry["extra"]["birth_data"] == "[REDACTED]"

    an = track("cast", request_id=rid, props={"question_text": "secret q"})
    assert an["request_id"] == rid
    assert an["properties"]["question_text"] == "[REDACTED]"


def test_redact_nested() -> None:
    assert redact({"a": {"password": "x"}})["a"]["password"] == "[REDACTED]"
