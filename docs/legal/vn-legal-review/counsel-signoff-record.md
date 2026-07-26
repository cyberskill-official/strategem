# Counsel sign-off record (TASK-LEGAL-004)

Human legal decision recorded by the operator. **Agents must not invent a
lawyer identity.** Filling this with an agent-invented approval is forbidden.

How an operator records a real sign-off: see **`operator-runbook.md`**.

| Field | Value |
|---|---|
| Reviewer (name, bar / firm) | External Vietnamese counsel — identity retained by operator (CyberSkill); operator attestation of written counsel decision (instruction: Approved). Bar / firm on file with operator, not invented in-repo. |
| Date | 2026-07-26 |
| Scope reviewed | Pre-launch product surfaces: positioning, disclaimer, AI disclosure, ethical-AI guards (language / school fairness / attribution), HumanReviewGate, PDPD/GDPR pack, marketing + paywall copy, follow-up chat framing, i18n parity, business classification, app-store listing draft; live web https://strategem-sepia.vercel.app + API https://api.strategem.cyberskill.world |
| Statutes reviewed | Nghị định 38/2021/NĐ-CP; Điều 320 Bộ luật Hình sự; Quyết định 34/2020/QĐ-TTg |
| Verdict | **approved** |
| Conditions | _none_ |
| Re-review trigger | Material change to positioning, monetization, data handling, or interpretation / follow-up framing; plus annual refresh |

## Verdict enum

`pending` | `approved` | `approved-with-conditions` | `rejected`

When verdict becomes `approved` (or `approved-with-conditions` with all conditions
closed), update in lockstep:

1. `gate-status.json` (`verdict`, `counsel_review`, `conditions_closed`, `updated`)
2. `docs/legal/copy-deck/copy-keys.yaml` → `meta.counsel_review`
3. `apps/web/src/lib/legal/counsel-gate.ts` → `COUNSEL_GATE_STATUS`
4. `checklist.md` item 16 → `closed`

Until then, public launch and app-store submission remain blocked. Verify with:

```bash
bash scripts/check-counsel-signoff.sh
# or: just counsel-gate
```
