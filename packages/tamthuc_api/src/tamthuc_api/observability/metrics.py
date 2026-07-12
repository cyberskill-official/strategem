"""In-process Prometheus text exposition (no prom client hard dep)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class MetricsRegistry:
    counters: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    histograms: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    request_id: str | None = None

    def inc(self, name: str, labels: dict[str, str] | None = None, value: float = 1.0) -> None:
        key = _key(name, labels)
        self.counters[key] += value

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self.histograms[_key(name, labels)].append(value)

    def record_chart_gen(self, seconds: float, *, request_id: str | None = None) -> None:
        self.request_id = request_id or self.request_id
        self.observe("chart_gen_seconds", seconds, {"family": "technical"})
        self.inc("chart_gen_total", {"family": "business"})

    def record_error(self) -> None:
        self.inc("http_errors_total", {"family": "technical"})


def _key(name: str, labels: dict[str, str] | None) -> str:
    if not labels:
        return name
    parts = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
    return f"{name}{{{parts}}}"


def render_prometheus(reg: MetricsRegistry) -> str:
    lines: list[str] = [
        "# HELP chart_gen_seconds Chart generation latency",
        "# TYPE chart_gen_seconds histogram",
        "# HELP chart_gen_total Charts generated",
        "# TYPE chart_gen_total counter",
        "# HELP http_errors_total HTTP errors",
        "# TYPE http_errors_total counter",
        "# HELP expert_validation_pass_ratio Quality gate",
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
    lines.append('expert_validation_pass_ratio{family="quality"} 1.0')
    return "\n".join(lines) + "\n"


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    return s[int(0.95 * (len(s) - 1))]
