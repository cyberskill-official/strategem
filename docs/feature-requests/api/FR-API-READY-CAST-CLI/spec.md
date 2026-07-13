---
id: API-READY
title: /ready probe + CAST_CLI presence
status: ready_to_test
class: product
priority: MUST
depends_on: []
---

# API-READY

## Goal
Operators can probe whether the API process is healthy and whether `CAST_CLI` is configured and executable. Optional strict mode fails readiness if CLI missing.

## §1
1. `GET /healthz` remains liveness-only (`status: ok`).
2. `GET /ready` returns structured `checks` including `cast_cli_configured`, `cast_cli_present`, `engine_mode`.
3. Env `READY_REQUIRE_CAST_CLI=1` → HTTP 503 when CLI not present/executable.
