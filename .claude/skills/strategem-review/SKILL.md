---
name: strategem-review
description: Review an in_review Tam Thuc Strategem task before sign-off - verify the FR acceptance criteria against the ledger evidence, re-run the accuracy and security gates yourself, check scope and sensitive paths, then set the task done or reject it. Also runs the per-phase sign-off gates. Use when reviewing an implemented strategem FR or PR, approving/verifying a task, or doing a P0-P3 phase sign-off (for example "review TT task QMDG-006", "strategem phase P0 sign-off", "can I mark CORE-006 done").
---

# Strategem - review an in_review task

The implementing agent flips `todo -> implementing -> in_review`. Only the reviewer flips `in_review -> done`. This skill is the reviewer's checklist. Do not rubber-stamp: re-run the accuracy- and security-critical gates yourself.

## 1. Per-task review

For each task in `in_review`:

1. Read the FR's section 4 (acceptance) and section 5 (verification) under `docs/feature-requests/<module>/`. Confirm every criterion has evidence in the matching `docs/feature-requests/LEDGER.md` entry.
2. Re-run the named gates yourself for anything security- or accuracy-critical:
   - Engines (CORE, QMDG, LN, TAT, RULE): run the oracle diff on a fresh sample. For CORE, run the sxwnl and tyme4py cross-check; a term error over 60 seconds or any pillar mismatch is a reject.
   - Envelope / contract (PLAT-002): run the cross-language round-trip and the schema-drift check.
   - Auth / security / data (AUTH, PLAT-003, PLAT-007, LEGAL-002): run the no-GUC RLS probe (expect zero rows), confirm birth data is encrypted at rest and absent from logs, confirm the erasure and export paths.
   - Interpretation (RAG, REPORT): confirm citations resolve, AIDisclosure is present, and no chart field (`ban` / `cach_cuc` / `lich_phap` / `co_truong_phai`) was written by the AI path; spot-check a handful of outputs for faithfulness.
   - Frontend (WEB, CHART): view it. Confirm the Vietnamese diacritics clip test, the deterministic-vs-AI visual split, and that cat/hung is never encoded by color alone.
3. Confirm the branch touched only what the FR scopes; check the "sensitive paths" line in the ledger entry.
4. Set `done` in `docs/feature-requests/backlog.yaml` (and the row in `IMPLEMENTATION_ORDER.md`), and push when a wave or phase closes.

## 2. Per-phase sign-off gates

Do not start the next phase until these pass (they are the phase exit gates in `IMPLEMENTATION_ORDER.md`):

- P0 closes only when the end-to-end demo passes live: sign in, cast a QiMen chart, see the 9-palace chart, the cach cuc, and a cited interpretation with the AIDisclosure badge - and the CORE-006 and QMDG-006 oracle gates are green in CI.
- P1 closes when LiuRen (LN-006) matches kinliuren, the Timing Optimizer produces scored windows, and a report exports.
- P2 closes when TaiYi (TAT-006) matches kintaiyi and the interpretation eval loop (RAG-006) is gating CI.
- P3 closes when auto-graded practice works against the engine and the security and compliance hardening pass is complete, with the LEGAL-004 counsel sign-off recorded before any public launch or app-store submission.

## 3. Reject mechanics

If a criterion fails, set the task back to `ready_to_implement` (or `blocked`) in `backlog.yaml` with a one-line reason in the ledger referencing the failing criterion. The implementing agent (the `strategem-implement` skill) picks it up again. Never set `done` on partial evidence, a red gate, or an unresolved sensitive-path concern.
