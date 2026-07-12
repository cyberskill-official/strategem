---
id: FR-LASO-001
title: Single source of truth for supported envelope versions
module: laso-envelope
class: improvement
status: done
owner: cyberos-e2e
---

# FR-LASO-001 - Single source of truth for supported envelope versions

## 1. Normative clauses

1. The set of supported `envelope_version` values MUST be defined once, as an importable module-level constant `SUPPORTED_ENVELOPE_VERSIONS: frozenset[int]` in `laso_envelope.models`, and MUST be re-exported from the package root (`laso_envelope`).
2. `require_supported_version` MUST decide acceptance solely by membership in `SUPPORTED_ENVELOPE_VERSIONS` (no inline literal set), and its `ValueError` message MUST list the supported versions.
3. Behaviour MUST be unchanged for the current supported set `{1}`: an envelope with `envelope_version == 1` is accepted; any other integer version raises `ValueError`.
4. Tests MUST assert: (a) `1 in SUPPORTED_ENVELOPE_VERSIONS`; (b) a v1 envelope is accepted by `require_supported_version`; (c) an unsupported version raises `ValueError` whose message names the supported set.

## 2. Scope

Touched: `packages/laso_envelope/src/laso_envelope/models.py`, `.../__init__.py`, `packages/laso_envelope/tests/`. Pure refactor to a single source of truth plus coverage; no schema, wire-format, or Rust-parity change.

## 3. Gate

Python lane, targeted: `uv run pytest -q packages/laso_envelope`. No behaviour change, so the cache-key / golden-parity tests must stay green.
