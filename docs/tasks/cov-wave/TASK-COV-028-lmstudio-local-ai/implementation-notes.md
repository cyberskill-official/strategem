# COV-028 implementation notes

## Landed

| artefact | path |
|----------|------|
| OpenAICompatibleLlm | `packages/tamthuc_rag/src/tamthuc_rag/llm.py` |
| llm_from_env factory | same (`LLM_BACKEND=stub\|openai_compatible\|lmstudio\|off`) |
| interpret wiring | `packages/tamthuc_rag/src/tamthuc_rag/interpret.py` uses `llm_from_env()` |
| Contract tests | `packages/tamthuc_rag/tests/test_openai_compatible_llm.py` |
| Compose env + host gateway | `deploy/compose/docker-compose.local.yml` |
| Runbook | `docs/deploy/local-docker-lmstudio.md` |

## Live LMStudio

- Host `:1234` was **down** at verification time — honest degraded path documented and mock contract tests cover success/unreachable.
- When operator starts LMStudio: set `LLM_MODEL` and re-probe `/v1/models`; no code change required.

## Tests

| suite | result |
|-------|--------|
| test_openai_compatible_llm (4) | pass |
| live LMStudio | skip / degraded (server not running) |

## Status

`ready_to_review` — **HITL required**. Agent will not set `done`. Client lands before COV-011 product default flip (per task §4 note).
