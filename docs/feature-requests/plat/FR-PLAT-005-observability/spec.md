---
id: FR-PLAT-005
title: "Observability - Prometheus + Grafana metrics (business, technical, quality), Sentry error tracking, Loki structured logs, PostHog/Mixpanel analytics, and Alertmanager/PagerDuty alerting on chart-gen p95 > 5s, error rate > 1%, LLM downtime, and DB connection issues"
module: PLAT
priority: MUST
status: testing
phase: P1
slice: 1
lang: iac/python
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-41, strategy 4.1, strategy 4.4, strategy RISK-5]
related_frs: [FR-PLAT-004, FR-PLAT-007, FR-PLAT-008, FR-API-001, FR-API-003, FR-RAG-007]
depends_on: [FR-PLAT-004]
blocks: [FR-PLAT-008]
new_paths:
  - deploy/observability/prometheus/prometheus.yml
  - deploy/observability/prometheus/rules/alerts.yml
  - deploy/observability/grafana/dashboards/business.json
  - deploy/observability/grafana/dashboards/technical.json
  - deploy/observability/grafana/dashboards/quality.json
  - deploy/observability/loki/loki-config.yml
  - deploy/observability/alertmanager/alertmanager.yml
  - deploy/observability/README.md
  - packages/tamthuc_api/tamthuc_api/observability/__init__.py
  - packages/tamthuc_api/tamthuc_api/observability/metrics.py
  - packages/tamthuc_api/tamthuc_api/observability/logging.py
  - packages/tamthuc_api/tamthuc_api/observability/sentry.py
  - packages/tamthuc_api/tamthuc_api/observability/analytics.py
  - packages/tamthuc_api/tests/test_metrics.py
  - docs/contracts/metrics-catalog.md
---

## §1 - Description (BCP-14 normative)

This FR is the observability stack: the metrics, dashboards, structured logs, error tracking, product analytics, and alerting that make the running platform legible. It extends the deployed environments FR-PLAT-004 defines with a Prometheus + Grafana metrics pipeline, Sentry error tracking, Loki log aggregation, PostHog/Mixpanel product analytics, and Alertmanager/PagerDuty alert routing. It owns the metric catalog, the dashboards, and the alert rules; it does NOT own the behaviors those alerts observe - resilience (FR-PLAT-008), rate limiting (FR-API-003), or security controls (FR-PLAT-007) - though it is the instrument that makes them measurable.

The platform SHALL expose Prometheus metrics across three families. Business metrics SHALL include queries/day, conversion, and retention (D1/D7/D30). Technical metrics SHALL include chart-generation latency (p50/p95/p99), LLM call latency, error rate, and database performance. Quality metrics SHALL include the expert-validation pass rate and NPS. Every metric SHALL carry stable labels (route, system/he, tier, engine_version) so a dashboard can slice by them. The instrumented services SHALL emit structured JSON logs shipped to Loki, and SHALL report unhandled exceptions to Sentry with a request-id that correlates a log line, a trace, and a Sentry issue. Product-analytics events (query cast, report viewed, sign-up, upgrade) SHALL flow to PostHog/Mixpanel behind a consent flag, and SHALL NOT carry sensitive personal data (birth_data, full question text) into the analytics sink (RISK-5).

Alerting SHALL be rule-driven and SHALL fire at minimum on: chart-generation p95 > 5s, error rate > 1%, LLM downtime (the LLM provider probe failing), and database connection issues (pool exhaustion or connection errors). Alerts SHALL route through Alertmanager to PagerDuty with a severity, a runbook link, and a deduplication key, and SHALL NOT fire into a silent channel. Metric cardinality SHALL be bounded: labels are a closed set, never free-form user input.

## §2 - Why this design (rationale for humans)

A platform that gives divination interpretations under legal constraints cannot be operated blind. The three metric families answer the three questions that matter: is the product growing (business), is it healthy (technical), and is it good (quality). Splitting them is deliberate - a green technical dashboard with a falling expert-validation pass rate is a product on fire that a pure-infra view would miss, and the quality family (validation pass rate, NPS) is exactly the signal the interpretation branch's correctness rides on (RISK-3, RISK-9). Keeping the quality metrics first-class, next to latency and error rate, is what makes interpretation regressions visible instead of anecdotal.

The specific alert thresholds are the operability floor, not decoration. Chart-generation p95 > 5s is the line where the casting path stops feeling instant; error rate > 1% is the line where something is systematically broken rather than a one-off; LLM downtime and DB connection issues are the two external-dependency failures that take the whole flow down, and they are precisely what FR-PLAT-008's circuit breaker and degradation react to - so PLAT-008 depends on this FR to see those transitions. Routing to PagerDuty with a runbook link rather than a chat message keeps an incident from being missed at 3am. Correlating logs, traces, and Sentry by request-id turns "the API is slow" into "this request, this route, this upstream, this stack" in one hop. Excluding sensitive data from the analytics sink keeps a growth tool from becoming a second breach surface.

## §3 - Contract (metrics / dashboards / alerts)

### Metric catalog (`docs/contracts/metrics-catalog.md`, emitted by `observability/metrics.py`)

| Family | Metric | Type | Labels |
|---|---|---|---|
| business | `tt_queries_total` | counter | route, he, tier |
| business | `tt_conversion_total` | counter | funnel_step, tier |
| business | `tt_retention_active_users` | gauge | cohort (d1/d7/d30) |
| technical | `tt_chart_generation_seconds` | histogram | he, engine_version |
| technical | `tt_llm_call_seconds` | histogram | provider, model |
| technical | `tt_request_errors_total` | counter | route, code |
| technical | `tt_db_query_seconds` | histogram | op, table |
| technical | `tt_db_pool_in_use` | gauge | pool |
| quality | `tt_expert_validation_pass_ratio` | gauge | he |
| quality | `tt_nps` | gauge | segment |

Histograms carry the buckets needed to compute p50/p95/p99. Chart-generation and LLM latency are measured at the orchestrator seam (FR-API-001), so they reflect the user-visible cast, not an internal sub-step.

### Alert rules (`deploy/observability/prometheus/rules/alerts.yml`)

```yaml
groups:
  - name: tamthuc-slo
    rules:
      - alert: ChartGenP95High
        expr: histogram_quantile(0.95, sum(rate(tt_chart_generation_seconds_bucket[5m])) by (le)) > 5
        for: 10m
        labels: { severity: warning }
        annotations: { runbook: "deploy/observability/README.md#chart-gen-latency" }
      - alert: ErrorRateHigh
        expr: sum(rate(tt_request_errors_total[5m])) / sum(rate(tt_requests_total[5m])) > 0.01
        for: 5m
        labels: { severity: critical }
      - alert: LLMDowntime            # provider probe failing
        expr: max_over_time(tt_llm_up[5m]) == 0
        for: 2m
        labels: { severity: critical }
      - alert: DBConnectionIssues     # pool exhaustion / connection errors
        expr: tt_db_pool_in_use / tt_db_pool_size > 0.9 or increase(tt_db_connection_errors_total[5m]) > 0
        for: 5m
        labels: { severity: critical }
```

### Structured logging (`observability/logging.py`) and error tracking (`observability/sentry.py`)

JSON logs `{ ts, level, request_id, route, principal_hash, msg, ... }` shipped to Loki; `request_id` is the correlation key across logs, metrics exemplars, and Sentry. Sentry captures unhandled exceptions with the same `request_id` and scrubs sensitive fields before send. No log line or Sentry event contains plaintext `birth_data` or full question text.

### Analytics (`observability/analytics.py`)

PostHog/Mixpanel events (`query_cast`, `report_viewed`, `signup`, `upgrade`) keyed by a pseudonymous id, gated on the analytics-consent flag (FR-LEGAL-002), carrying no sensitive payload.

## §4 - Acceptance criteria

1. The API and engine service expose a Prometheus scrape endpoint carrying all three metric families; a scrape returns the business, technical, and quality metrics with their documented labels and bounded cardinality.
2. Grafana loads the three dashboards (business, technical, quality) and each renders from live metrics: queries/day and retention D1/D7/D30 on business; chart-gen p50/p95/p99, LLM latency, error rate, and DB performance on technical; expert-validation pass rate and NPS on quality.
3. The four alert rules fire under synthetic load: chart-gen p95 driven above 5s fires `ChartGenP95High`; forced errors above 1% fire `ErrorRateHigh`; an LLM probe failure fires `LLMDowntime`; a saturated pool fires `DBConnectionIssues`; each routes to PagerDuty with a severity and a runbook link.
4. A request's `request_id` correlates its structured log line in Loki, its metric exemplar, and its Sentry issue; the same id appears in all three.
5. No metric label, log line, Sentry event, or analytics event contains plaintext `birth_data` or full question text; a redaction test asserts absence across all sinks.
6. Alerts route through Alertmanager to PagerDuty (no silent channel); a silenced/misrouted alert is caught by a routing test.

## §5 - Verification

- `tests/test_metrics.py`: asserts each catalog metric is registered with the right type and labels; asserts cardinality is bounded (labels are a closed enum, not free-form input); asserts the p95 histogram buckets support the 5s threshold.
- A dashboards-as-code check: the three Grafana JSON dashboards load and their panel queries reference only metrics in the catalog (a drift check fails on an undefined metric).
- An alert-rule unit test (`promtool test rules`) drives each of the four expressions across pass/fire fixtures.
- A redaction test feeds a request carrying birth_data + question text and asserts none of it reaches logs, Sentry, metrics labels, or analytics.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_api`, `pytest packages/tamthuc_api`; `promtool check rules`; the alert YAML and dashboards lint in the FR-PLAT-004 pipeline.

## §6 - Implementation skeleton

1. `observability/metrics.py`: register the three metric families (prometheus_client), instrument the orchestrator seam for chart-gen and LLM latency, the exception path for error rate, the repositories for DB performance.
2. `observability/logging.py`: structured JSON logging with `request_id` propagation; ship to Loki.
3. `observability/sentry.py`: Sentry init with a before-send scrubber; wire the `request_id` scope.
4. `observability/analytics.py`: PostHog/Mixpanel client behind the consent flag; the event schema with no sensitive payload.
5. `deploy/observability/*`: Prometheus scrape config, the alert rules, the three Grafana dashboards, Loki config, Alertmanager -> PagerDuty routing; the runbook `README.md`.
6. Wire the metrics endpoint and middleware into `app.py`; document the catalog in `docs/contracts/metrics-catalog.md`.

## §7 - Dependencies

Depends on FR-PLAT-004 (the deployed staging/production environments this instruments, and the pipeline that lints the alert YAML and dashboards). Blocks FR-PLAT-008 (resilience: the circuit-breaker and degradation transitions must be observable here, and PLAT-008's health signals feed these alerts). Instruments FR-API-001 (the orchestrator seam where chart-gen and LLM latency are measured), FR-API-003 (rate-limit and abuse events surface as metrics and alerts), and FR-RAG-007 (LLM fallback state feeds the `LLMDowntime` signal). Coordinates with FR-PLAT-007 (security events are audited and alertable) and FR-LEGAL-002 (the analytics-consent flag).

## §8 - Example payloads

```json
// structured log line (to Loki) - correlated by request_id, no sensitive payload
{ "ts": "2026-07-08T12:00:00Z", "level": "info", "request_id": "req_abc",
  "route": "/api/v1/calculate/qimen", "he": "ky_mon", "tier": "Premium",
  "chart_gen_ms": 820, "llm_ms": 1400, "msg": "query served" }
```

```json
// PagerDuty alert (via Alertmanager) - severity + runbook, dedup key
{ "alert": "ChartGenP95High", "severity": "warning", "value_s": 6.2,
  "runbook": "deploy/observability/README.md#chart-gen-latency", "dedup_key": "chartgen-p95" }
```

## §9 - Open questions

- Analytics vendor: PostHog (self-hostable, open) vs Mixpanel (managed). Default: PostHog at MVP for data-residency control (VN PDPD context), keeping the event schema vendor-neutral so a swap is a client change, not a schema change. Confirm with FR-LEGAL-002.
- Tracing depth: metrics + logs + Sentry now, full distributed tracing (OpenTelemetry spans) later. Default: emit a `request_id` and metric exemplars now so traces can be added without re-instrumenting; a full OTel backend (Tempo/Jaeger) is a later step.
- Where the expert-validation pass rate is computed. Default: FR-RAG-006's eval loop produces the number and this FR exposes it as `tt_expert_validation_pass_ratio`; until RAG-006 lands, the gauge reads from the KB-002 validation set run.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Blind operation | no metrics/alerts on a legal-sensitive surface | forbidden; the three metric families and the four alert rules are the floor before P1 exit |
| Sensitive data in telemetry | birth_data / question text in a label, log, Sentry event, or analytics | scrubbed at every sink; the redaction test asserts absence (RISK-5) |
| Silent alert | alert routed to a dead channel or none | Alertmanager -> PagerDuty with severity + runbook; a routing test catches a silent path |
| Cardinality explosion | free-form input used as a metric label | labels are a closed enum; the cardinality test rejects unbounded labels |
| Quality invisibility | only infra metrics, no validation pass rate / NPS | the quality family is first-class; the quality dashboard renders it |
| Uncorrelated signals | logs, metrics, Sentry cannot be joined | one `request_id` correlates all three; the correlation test asserts it |

## §11 - Notes

This FR is the instrument, not the machine: it measures the platform but changes no product behavior. Hold three disciplines - three metric families (business, technical, quality) so growth, health, and correctness are all visible; sensitive data never in telemetry (RISK-5); and no silent alerts, everything routes to PagerDuty with a runbook. The Python instrumentation lives in the `tamthuc_api` package and the IaC (Prometheus/Grafana/Loki/Alertmanager config) under `deploy/observability/`, reflecting the iac/python split. FR-PLAT-008 builds directly on this: its circuit-breaker and degradation transitions are only useful if they are observable here.
