# Operator runbook — LEGAL-004 counsel sign-off (RISK-4)

This runbook is for a **human operator** coordinating **Vietnamese counsel**.
Agents must not invent a lawyer identity, date, or approval. Leaving verdict
`pending` is the correct default until real counsel completes review.

## What “done” means

Public launch and app-store submission are unblocked only when:

1. Counsel has filled `counsel-signoff-record.md` with a real reviewer identity.
2. Verdict is `approved` or `approved-with-conditions` (all listed conditions closed).
3. `gate-status.json` mirrors that verdict.
4. LEGAL-001 deck marker `meta.counsel_review` in `docs/legal/copy-deck/copy-keys.yaml` matches.
5. In-product TS mirror `apps/web/src/lib/legal/counsel-gate.ts` matches (so the banner can clear).
6. `bash scripts/check-counsel-signoff.sh` (or `just counsel-gate`) exits **0**.

Until then, `docs/deploy/SHIP_CHECKLIST.md` must not claim launch-ready, and
`just ship-ready` must fail.

## Preconditions (operator)

1. Procure external VN counsel (culture / advertising law specialist preferred).
2. Hand counsel this packet:
   - `checklist.md` (all rows)
   - `statute-map.md`
   - `sign-off-gate.md`
   - Copy deck under `docs/legal/copy-deck/`
   - Ethical-AI docs under `docs/legal/ethical-ai/`
   - PDPD pack under `docs/legal/pdpd-gdpr/`
   - Live product surfaces: cast, results, report, follow-up chat, pricing if any
   - Draft app-store listing copy (if submitting)
3. Walk checklist items 1–15 with counsel; mark Status `closed` or `deferred`
   (deferred items become conditions on a conditional verdict).

## Recording a real sign-off

### Step A — Fill the record

Edit **only** `docs/legal/vn-legal-review/counsel-signoff-record.md`:

| Field | What to put |
|---|---|
| Reviewer (name, bar / firm) | Real counsel name + bar number or firm |
| Date | ISO date of the review decision (`YYYY-MM-DD`) |
| Scope reviewed | Concrete surfaces reviewed (URLs / builds / copy versions) |
| Statutes reviewed | Keep the three named statutes; add others counsel cites |
| Verdict | Exactly one of: `approved` \| `approved-with-conditions` \| `rejected` |
| Conditions | Bullet list; empty only if verdict is `approved` |
| Re-review trigger | Keep material-change + annual refresh; counsel may tighten |

Do **not** set Verdict to `approved` without counsel’s explicit written decision.

### Step B — Flip machine status

Edit `docs/legal/vn-legal-review/gate-status.json`:

```json
{
  "task": "LEGAL-004",
  "counsel_review": "approved",
  "verdict": "approved",
  "note": "Signed off by <counsel> on <YYYY-MM-DD>. See counsel-signoff-record.md.",
  "record": "docs/legal/vn-legal-review/counsel-signoff-record.md",
  "checklist": "docs/legal/vn-legal-review/checklist.md",
  "statute_map": "docs/legal/vn-legal-review/statute-map.md",
  "gate": "docs/legal/vn-legal-review/sign-off-gate.md",
  "updated": "<YYYY-MM-DD>",
  "conditions_closed": true
}
```

Rules:

- `verdict` must match the record Verdict field (case-sensitive enum above).
- For `approved-with-conditions`, set `"conditions_closed": true` only after every
  listed condition is actually closed; otherwise leave `false` (script fails).
- For `rejected` or still working, leave `verdict` as `pending` / `rejected`
  and do **not** claim launch-ready.

### Step C — Align LEGAL-001 deck marker

In `docs/legal/copy-deck/copy-keys.yaml`, under `meta:`:

```yaml
counsel_review: approved   # was pending
```

### Step D — Align in-product gate (banner)

In `apps/web/src/lib/legal/counsel-gate.ts`, set:

```ts
counsel_review: "approved",
verdict: "approved", // or "approved-with-conditions"
```

This clears `CounselReviewBanner` once the app rebuilds. Do not change it before
Steps A–B.

### Step E — Close checklist item 16

In `checklist.md`, set item 16 Status to `closed`. Confirm items 1–15 are
`closed` or covered by open conditions that are themselves closed.

### Step F — Verify the machine gate

```bash
bash scripts/check-counsel-signoff.sh
# or
just counsel-gate
just ship-ready
```

Exit 0 means the release/ship path may proceed on the legal gate. Exit non-zero
means launch remains blocked — fix the mismatch; do not bypass.

## Re-opening the gate

Re-open (set verdict back to `pending`, restore deck + TS mirrors, reopen item 16)
when any re-review trigger fires: material change to positioning, monetization,
data handling, interpretation / follow-up framing, or the annual refresh.

## What agents must not do

- Invent counsel names, firms, bar numbers, or approval dates
- Set `verdict` / `counsel_review` to `approved*` without a human counsel decision
- Delete or weaken `scripts/check-counsel-signoff.sh` to greenwash launch
- Mark `SHIP_CHECKLIST.md` launch-ready while the script exits non-zero
