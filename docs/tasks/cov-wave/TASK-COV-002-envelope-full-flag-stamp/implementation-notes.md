# COV-002 implementation notes

## Landed

### Rust engines (cast-cli path)

- `crates/cyberos-qimen/src/engine.rs` — `lich_phap.co_lich_phap` + existing `co_truong_phai` (full QiMenFlags)
- `crates/cyberos-luchnham/src/engine.rs` — calendar + school stamp
- `crates/cyberos-thaiat/src/engine.rs` — calendar + school stamp

### Python API client

- `packages/tamthuc_api/src/tamthuc_api/clients/engine.py`
- `StubEngineClient`, `_cast_via_cli`, `_cast_local` always stamp both objects
- Missing request flags → explicit `{stamped: "default"|true, source: ...}` (no silent empty omit)

### Tests

| suite | result |
|-------|--------|
| `cyberos-qimen` flag_stamp_cov002 | pass |
| `cyberos-luchnham` flag_stamp_cov002 | pass |
| `cyberos-thaiat` flag_stamp_cov002 | pass |
| `packages/tamthuc_api/tests/test_flag_stamp_cov002.py` | pass |

Evidence (operator scratch): `cov002-tests.log`, `cast-cli-stamps.jsonl`.

## §1 AC mapping

1. Full school + calendar stamps on cast-cli + LocalEngineClient — yes
2. Missing flag → explicit default + stamp — yes
3. Flags on API chart payload (`charts.*.co_truong_phai`, `lich_phap.co_lich_phap`) — yes (after image rebuild with stamp engines)
4. Tests for all three he — yes

## Status

`ready_to_review` — **HITL required** before `ready_to_test` / `done`. Agent will not set `done`.
