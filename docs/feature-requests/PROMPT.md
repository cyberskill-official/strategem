# Tam Thuc Strategem - implementation agent prompt and review protocol

## Part A - the agent trigger prompt

Paste this into a fresh implementation session (fill the task id, or leave it blank to take the next eligible task).

---

You are an implementation agent for the Tam Thuc Strategem product. Work one task to a reviewable state, then stop.

Context you must load first:
1. `docs/strategy/tam-thuc-unified-plan-2026-07-08.md` - the rationale, architecture spine, module taxonomy, and invariants. Read the sections your task's FR cites in `refs`.
2. `docs/feature-requests/backlog.yaml` - task status and eligibility. `docs/feature-requests/IMPLEMENTATION_ORDER.md` - the human view.
3. The task's FR under `docs/feature-requests/<module>/` - this is your spec. Implement to its section 4 acceptance criteria and section 5 verification.
4. `docs/feature-requests/README.md` - conventions, and the two exemplar FRs (`FR-PLAT-002`, `FR-CORE-001`) if you need the shape.

Pick the task:
- If given a task id, use it. Otherwise take the next eligible task in IMPLEMENTATION_ORDER.md order (phase, dependency spine, then id). Eligible = FR is `ready_to_implement`, status not `done`, every `depends_on` is `done`.
- If the task's `body` is `planned` (the FR is a `draft`), your first unit of work is to AUTHOR the FR body: read the module README plus the cited primary source (the Claude volume or Grok doc named in the strategy coverage map), follow the two exemplars exactly (frontmatter + section 1-11), write the FR file, set its status to `ready_to_implement`, and STOP for review before implementing - unless the operator told you to proceed through both authoring and implementation.

Do the work:
- One task = one branch `auto/tt-<id-lowercase>`. One task per commit where practical; message `<ID>: <title>`.
- Honor the safety invariants in `README.md` and strategy section 4.4. In particular: engines keep the la so JSON envelope exact and stamp every school flag; interpretation code never writes `ban` / `cach_cuc` / `lich_phap` / `co_truong_phai` and keeps citation + AIDisclosure + HumanReviewGate; never log birth data or question text.
- Run the gates for your language (README.md "Gates"). Engines additionally run the oracle cross-check (kinqimen / kinliuren / kintaiyi / sxwnl / tyme4py) per the FR. A calendar term off by more than 60 seconds is a stop-ship.

Record and hand off:
- Update the task status in `backlog.yaml` (and the row in `IMPLEMENTATION_ORDER.md`) to `implementing` when you start and `in_review` when every acceptance criterion passes with evidence. Do this in the same commit as the work.
- Append one entry to `LEDGER.md` in the format defined there (branch, commits, status transition, gates run and results, evidence, sensitive paths, notes).
- Stop at the operator edges: do not push to main, deploy, rotate a secret, or run a destructive migration on shared data. Hand those to the operator with a clear note.
- If you cannot finish inside a reasonable budget (about 5 consecutive gate failures), set the task back to `ready_to_implement` with a `blocked_note`, record why in the ledger, and move on.

Report back: the task id, the branch, the commits, gate results, what a reviewer should check, and any follow-ups (file them as new tasks, do not scope-creep the current one).

---

## Part B - the human review protocol

The agent flips `todo -> implementing -> in_review`. Only you flip `in_review -> done`.

For each `in_review` task:
1. Read the FR's section 4 (acceptance) and section 5 (verification). Confirm every criterion has evidence in the ledger entry.
2. Run the named gates yourself for anything security- or accuracy-critical:
   - Engines (CORE, QMDG, LN, TAT, RULE): run the oracle diff yourself on a fresh sample. For CORE, run the sxwnl and tyme4py cross-check; a >60s term error or any pillar mismatch is a reject.
   - Envelope/contract (PLAT-002): run the cross-language round-trip and the schema-drift check.
   - Auth/security/data (AUTH, PLAT-003, PLAT-007, LEGAL-002): run the no-GUC RLS probe, confirm birth data is encrypted at rest and absent from logs, confirm erasure/export paths.
   - Interpretation (RAG, REPORT): confirm citations resolve, AIDisclosure is present, and no chart field was written by the AI path; spot-check a handful of outputs for faithfulness.
   - Frontend (WEB, CHART): view it; confirm the diacritics clip test, the deterministic-vs-AI visual split, and cat/hung not encoded by color alone.
3. Confirm the branch touched only what the FR scopes; check the "sensitive paths" line in the ledger entry.
4. Set `done` in `backlog.yaml`, and push when a wave or phase closes.

Per-phase sign-off gates (do not start the next phase until these pass):
- P0 closes only when the end-to-end demo passes live (IMPLEMENTATION_ORDER.md P0 exit gate): sign in, cast a QiMen chart, see the 9-palace chart, the cach cuc, and a cited interpretation with AIDisclosure - and CORE-006 and QMDG-006 oracle gates are green in CI.
- P1 closes when LiuRen (LN-006) matches kinliuren, the Timing Optimizer produces scored windows, and a report exports.
- P2 closes when TaiYi (TAT-006) matches kintaiyi and the interpretation eval loop (RAG-006) is gating CI.
- P3 closes when auto-graded practice works against the engine and the security/compliance hardening pass is complete, with LEGAL-004 counsel sign-off recorded before any public launch.

Reject mechanics: set the task back to `ready_to_implement` (or `blocked`) with a one-line reason in the ledger referencing the failing criterion. The agent picks it up again.
