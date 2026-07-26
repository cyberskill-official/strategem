# Pre-launch checklist (TASK-LEGAL-004)

Each item must be closed (or explicitly deferred with counsel conditions) before
public launch or app-store submission. Owner tasks are the evidence pointers.

**Status values:** `open` | `deferred` | `closed`  
Agents and operators update Status from evidence; only Vietnamese counsel may
close item 16 (sign-off) and flip `gate-status.json`.

Sources: TASK-LEGAL-004 spec; Claude-07 s4.1–s4.3 / strategy §7; Grok ethics
(disclaimer, anti-destiny, citations).

| # | Item | Owner task | Evidence | Status |
|---|---|---|---|---|
| 1 | Positioning copy in-product (heritage education, not fortune-telling) | LEGAL-001 | `docs/legal/positioning-language-rules.md`, `docs/legal/copy-deck/` | open |
| 2 | Disclaimer at point of use (cast / results / report) | WEB-002 / WEB-003 | Query form + results disclaimer slots | open |
| 3 | AI-limits copy keyed for AIDisclosureBadge | LEGAL-001 | `docs/legal/copy-deck/ai-disclosure.md`, `copy-keys.yaml` | open |
| 4 | Forbidden lexicon enforced (certain-future / medical / legal-financial / fear-dependency) | LEGAL-001 / LEGAL-003 | `docs/legal/lexicon-do-dont.md`, RAG framing guard | open |
| 5 | Ethical-AI checks active over RAG / follow-up output | LEGAL-003 | `docs/legal/ethical-ai/`, `tamthuc_rag.ethics` | open |
| 6 | School fairness (`co_truong_phai` stamped; no one-school absolutism) | LEGAL-003 / PLAT-002 | `docs/legal/ethical-ai/school-fairness.md` | open |
| 7 | Source attribution (Han + transliteration + dich on citations) | LEGAL-003 / KB-003 / WEB-003 | `docs/legal/ethical-ai/source-attribution.md` | open |
| 8 | HumanReviewGate routes medium findings; high findings block | RAG-004 / LEGAL-003 | HumanReviewGate + ethics policy | open |
| 9 | Data-protection pack + consent + DSAR contracts (PDPD / GDPR) | LEGAL-002 | `docs/legal/pdpd-gdpr/` | open |
| 10 | Paywall / pricing / monetization language is decision-support, not superstition-for-profit | LEGAL-004 | statute-map (Điều 320); pricing / paywall copy | open |
| 11 | Marketing / ad copy reviewed against Nghị định 38 | LEGAL-004 | statute-map.md + counsel notes | open |
| 12 | Follow-up chat framing reviewed (no certain-future / advice verdicts) | LEGAL-003 / WEB | Follow-up UI + ethics over chat replies | open |
| 13 | i18n copy parity (vi / en / zh) matches positioning deck | WEB-006 / WEB-008 | `apps/web/src/messages/` | open |
| 14 | Business scope / registration classification vs Quyết định 34 | LEGAL-004 | statute-map.md; counsel notes | open |
| 15 | App-store listing copy reviewed (Apple / Google divination policy) | LEGAL-004 | counsel scope; store listing drafts | open |
| 16 | Counsel sign-off recorded (verdict approved, conditions closed) | LEGAL-004 | `counsel-signoff-record.md` | open |

## Machine gate

`scripts/check-counsel-signoff.sh` (also `just counsel-gate`) fails while
`gate-status.json` verdict is `pending` / absent / `rejected`, or while the
record and LEGAL-001 `counsel_review` markers disagree.

Public launch and app-store submission stay blocked until item 16 is closed by
a human counsel sign-off. See `operator-runbook.md`.
