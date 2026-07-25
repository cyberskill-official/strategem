"""TT-022: cast-cli fallback logging, metrics, fail-closed."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from tamthuc_api.clients.engine import (
    CastCliRequiredError,
    LocalEngineClient,
)
from tamthuc_api.observability.metrics import MetricsRegistry, render_prometheus


def _failing_cli(tmp_path: Path) -> str:
    script = tmp_path / "cast-cli-fail"
    script.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    script.chmod(0o755)
    return str(script)


def _ok_cli(tmp_path: Path) -> str:
    # Minimal JSON envelope on stdout
    script = tmp_path / "cast-cli-ok"
    script.write_text(
        "#!/bin/sh\n"
        'echo \'{"envelope_version":1,"he":"ky_mon","dau_vao":{},'
        '"lich_phap":{},"ban":{},"cach_cuc":[],"co_truong_phai":{},'
        '"provenance":{"engine":"qmdg","engine_version":"cli"}}\''
        "\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return str(script)


def test_cast_cli_success_stamps_engine_source(tmp_path: Path) -> None:
    eng = LocalEngineClient(_ok_cli(tmp_path))
    out = eng.cast("qimen", {"datetime": "2004-01-01T10:30:00", "tz": "+07:00"})
    assert out["provenance"]["engine_source"] == "cast_cli"
    assert out["provenance"]["engine"] == "qmdg"
    assert eng.last_engine_source == "cast_cli"


def test_cast_cli_failure_falls_back_logs_and_metrics(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("READY_REQUIRE_CAST_CLI", raising=False)
    monkeypatch.setenv("ENV", "development")
    metrics = MetricsRegistry()
    eng = LocalEngineClient(_failing_cli(tmp_path), metrics=metrics)
    with caplog.at_level(logging.WARNING, logger="tamthuc_api.clients.engine"):
        out = eng.cast("qimen", {"datetime": "2004-01-01T10:30:00", "tz": "+07:00"})
    assert out["provenance"]["engine_source"] == "local_fallback"
    assert out["provenance"]["engine"] == "qmdg"
    assert "cast_cli.fallback" in caplog.text or "CalledProcessError" in caplog.text
    body = render_prometheus(metrics)
    assert "cast_cli_fallback_total" in body


def test_cast_cli_failure_fail_closed_when_required(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("READY_REQUIRE_CAST_CLI", "1")
    monkeypatch.setenv("APP_ENV", "production")
    eng = LocalEngineClient(_failing_cli(tmp_path), metrics=MetricsRegistry())
    with pytest.raises(CastCliRequiredError):
        eng.cast("qimen", {"datetime": "2004-01-01T10:30:00", "tz": "+07:00"})
