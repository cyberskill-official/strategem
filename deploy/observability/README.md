# Observability (TASK-PLAT-005)

Prometheus scrapes `/metrics` on API + engine. Grafana dashboards under `grafana/dashboards/`. Alerts in `prometheus/rules/alerts.yml` route via Alertmanager → PagerDuty.

## Redaction

`tamthuc_api.observability.logging.redact` strips birth_data / question text from logs, Sentry extras, and analytics props. `request_id` correlates log ↔ metric exemplar ↔ Sentry.
