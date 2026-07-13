# Monitoring & alerting (COV-021)

## Metrics endpoint

```bash
curl -sS "$API_BASE/metrics"
```

Key series:

| Metric | Meaning |
|--------|---------|
| `cast_latency_seconds_p95{system,engine_mode}` | Cast p95 by system + mode |
| `cast_total{system,engine_mode,result}` | Cast attempts |
| `cast_errors_total` | Cast failures |
| `ready_failures_total{reason}` | `/ready` failures when CAST_CLI required |

## Alert ideas (log / Prometheus)

1. `ready_failures_total` increases while `READY_REQUIRE_CAST_CLI=1` → page on-call.
2. `cast_latency_seconds_p95` > 5s for 5m → investigate engine/CLI.
3. `cast_errors_total` / `cast_total` > 5% → error budget burn.

## Error budget (product)

- Target: 99% successful casts over 30d for free cast path.
- Burn alerts fire on multi-window rates (document in your Grafana/Prom rules).
