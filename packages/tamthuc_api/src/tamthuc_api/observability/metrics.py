"""In-process Prometheus text exposition (no prom client hard dep)."""

from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class MetricsRegistry:
    counters: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    histograms: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    gauges: dict[str, float] = field(default_factory=dict)
    request_id: str | None = None

    def inc(self, name: str, labels: dict[str, str] | None = None, value: float = 1.0) -> None:
        key = _key(name, labels)
        self.counters[key] += value

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self.histograms[_key(name, labels)].append(value)

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self.gauges[_key(name, labels)] = value

    def record_chart_gen(self, seconds: float, *, request_id: str | None = None) -> None:
        self.request_id = request_id or self.request_id
        self.observe("chart_gen_seconds", seconds, {"family": "technical"})
        self.inc("chart_gen_total", {"family": "business"})

    def record_cast(
        self,
        seconds: float,
        *,
        system: str,
        engine_mode: str = "unknown",
        ok: bool = True,
    ) -> None:
        """COV-021: cast latency by system + engine_mode."""
        labels = {"system": system, "engine_mode": engine_mode, "family": "product"}
        self.observe("cast_latency_seconds", seconds, labels)
        self.inc("cast_total", {**labels, "result": "ok" if ok else "error"})
        if not ok:
            self.inc("cast_errors_total", labels)

    def record_cast_fallback(self, *, system: str, reason: str) -> None:
        """TT-022: cast-cli failed; fell back to local deterministic engine."""
        self.inc(
            "cast_cli_fallback_total",
            {"system": system, "reason": reason, "family": "ops"},
        )

    def record_ready_failure(self, reason: str = "cast_cli_missing") -> None:
        """COV-021: alert signal when /ready fails under READY_REQUIRE_CAST_CLI."""
        self.inc("ready_failures_total", {"reason": reason, "family": "ops"})

    def record_request(self, *, method: str, path: str, status: int) -> None:
        """TT-017: total HTTP requests (denominator for ErrorRateHigh)."""
        self.inc(
            "http_requests_total",
            {
                "method": method,
                "path": _normalize_path(path),
                "status": str(status),
                "family": "technical",
            },
        )

    def record_error(self) -> None:
        self.inc("http_errors_total", {"family": "technical"})


def _normalize_path(path: str) -> str:
    # Collapse UUIDs so cardinality stays bounded.
    parts = []
    for p in path.split("/"):
        if len(p) == 36 and p.count("-") == 4:
            parts.append(":id")
        else:
            parts.append(p)
    return "/".join(parts) or "/"


def _key(name: str, labels: dict[str, str] | None) -> str:
    if not labels:
        return name
    parts = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
    return f"{name}{{{parts}}}"


def expert_validation_pass_ratio() -> float | None:
    """Optional quality gauge from env; omit when unset (no fake 1.0).

    Set EXPERT_VALIDATION_PASS_RATIO=0.0..1.0 when a real eval loop writes it.
    """
    raw = os.environ.get("EXPERT_VALIDATION_PASS_RATIO", "").strip()
    if not raw:
        return None
    try:
        v = float(raw)
    except ValueError:
        return None
    if v < 0.0 or v > 1.0:
        return None
    return v


def render_prometheus(reg: MetricsRegistry) -> str:
    lines: list[str] = [
        "# HELP chart_gen_seconds Chart generation latency",
        "# TYPE chart_gen_seconds histogram",
        "# HELP chart_gen_total Charts generated",
        "# TYPE chart_gen_total counter",
        "# HELP cast_latency_seconds Cast path latency by system/engine_mode",
        "# TYPE cast_latency_seconds histogram",
        "# HELP cast_total Cast attempts",
        "# TYPE cast_total counter",
        "# HELP cast_errors_total Cast failures",
        "# TYPE cast_errors_total counter",
        "# HELP cast_cli_fallback_total Cast-cli failures that fell back to local",
        "# TYPE cast_cli_fallback_total counter",
        "# HELP ready_failures_total /ready failures (CAST_CLI gate)",
        "# TYPE ready_failures_total counter",
        "# HELP http_requests_total HTTP requests",
        "# TYPE http_requests_total counter",
        "# HELP http_errors_total HTTP errors",
        "# TYPE http_errors_total counter",
        "# HELP expert_validation_pass_ratio Quality gate (optional)",
        "# TYPE expert_validation_pass_ratio gauge",
    ]
    for k, v in sorted(reg.counters.items()):
        lines.append(f"{k} {v}")
    for k, vals in sorted(reg.histograms.items()):
        if not vals:
            continue
        s = sorted(vals)
        p95 = s[int(0.95 * (len(s) - 1))] if s else 0.0
        base = k.split("{", 1)[0]
        labels = ""
        if "{" in k:
            labels = "{" + k.split("{", 1)[1]
        lines.append(f"{base}_p95{labels} {p95}")
        lines.append(f"{base}_count{labels} {len(s)}")
    for k, v in sorted(reg.gauges.items()):
        lines.append(f"{k} {v}")
    ratio = expert_validation_pass_ratio()
    if ratio is not None:
        lines.append(f'expert_validation_pass_ratio{{family="quality"}} {ratio}')
    return "\n".join(lines) + "\n"


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    return s[int(0.95 * (len(s) - 1))]
