# COV-011 implementation notes

## Landed

| artefact | path |
|----------|------|
| INTERPRET_MODE config | `packages/tamthuc_rag/src/tamthuc_rag/config.py` |
| LocalRagClient modes | `packages/tamthuc_api/src/tamthuc_api/clients/rag.py` |
| HumanReviewGate hook | same (`process_interpretation` for restricted) |
| Tests | `packages/tamthuc_api/tests/test_interpret_mode_cov011.py` |

## Behaviour

- `INTERPRET_MODE=rag|template` (default rag when vector backend configured).
- Template: engine-grounded copy + honest badge (`template-engine`, not live RAG).
- RAG: uses `llm_from_env` + pattern citation chunks; refuses free-form when no sources.
- Restricted question types → HumanReviewGate pending/withheld path.

## Status

`ready_to_review` — **HITL required**. Agent will not set `done`.
