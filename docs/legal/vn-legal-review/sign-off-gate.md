# Hard counsel sign-off gate (TASK-LEGAL-004 / RISK-4)

## Rule

**No public launch** and **no app-store submission** while counsel sign-off is
pending or rejected. A conditional sign-off (`approved-with-conditions`) lists
blocking conditions that MUST be closed before launch.

## Process

1. Counsel reviews against `statute-map.md` and `checklist.md`.
2. Counsel fills `counsel-signoff-record.md` (reviewer, date, scope, statutes,
   verdict, conditions, re-review trigger).
3. Flip `gate-status.json`, LEGAL-001 `counsel_review` (`copy-keys.yaml`), and
   the in-product mirror (`apps/web/src/lib/legal/counsel-gate.ts`) **only** via
   that record — see `operator-runbook.md`.
4. Release / app-store step runs `scripts/check-counsel-signoff.sh` or
   `just counsel-gate` / `just ship-ready` — exit non-zero blocks the step.
5. Material feature changes touching positioning, monetization, data handling, or
   follow-up chat framing re-open the gate (see re-review trigger on the record).

## In-product hook

The web shell renders `CounselReviewBanner` (`data-testid="counsel-review-gate"`)
while verdict is not approved. The banner does **not** claim legal sign-off has
occurred; it surfaces that launch remains blocked.

## Operator how-to

Step-by-step recording instructions (which files, which fields, how the script
flips to pass): **`operator-runbook.md`**. Agents must not perform the sign-off.

## Status today

`counsel_review: approved` — recorded 2026-07-26 (see `counsel-signoff-record.md`
and `gate-status.json`). Re-open on material-change / annual refresh triggers.
