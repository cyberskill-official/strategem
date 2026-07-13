# COV-001 implementation notes

## Landed

- Golden fixtures: qimen 36, liuren 30, taiyi 24 (`*_cert_v1.csv`)
- Multi-year tiet khi: 120 terms (`tietkhi_cert_multiyear.csv`)
- Integration tests: `certification_suite` / `tietkhi_certification`
- CI: `.github/workflows/oracle-certification.yml`
- Report: `docs/status/oracle/report.json` + README

## Oracle honesty

`oracle_source=engine_golden_v1+cast_cli` — deterministic regression goldens from current engines + cast-cli. External kin* libraries remain partial module fixtures; this FR is the product-scale certification gate for dual-benchmark 100%.

## Status

`ready_to_review` — **HITL required** before `ready_to_test` / `done`. Agent will not set `done`.
