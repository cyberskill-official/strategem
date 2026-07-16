# LEGAL - legal, ethics, compliance

The legal, ethical, and cultural guardrails that are product-defining for Tam Thuc Strategem, not add-ons: the in-product disclaimer and positioning language, the PDPD/GDPR compliance pack, the ethical-AI and cultural-sensitivity rules, and the VN counsel sign-off gate before launch. 4 tasks, ~30 engineering-hours, P0 disclaimer then P1 compliance. Source of rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (section 7, RISK-4, RISK-5) and Claude 07 (legal/ethics) + Grok 19,25. Language is doc plus Python where a contract needs code (erasure/export). Implementation order and trigger: `../IMPLEMENTATION_ORDER.md` + `../PROMPT.md`.

The one framing that governs the whole module: the product is heritage education and structured decision support, never fortune-telling or destiny prediction. The same classical method framed one way is lawful and respectful; framed as guaranteed prediction it is the RISK-4 legal exposure the module exists to avoid.

## tasks

| task | Pri | Phase | h | depends_on | Spec | Title |
|---|---|---|--:|---|---|---|
| LEGAL-001 | MUST | P0 | 6 | WEB-001 | [TASK-LEGAL-001](TASK-LEGAL-001-disclaimer-positioning/spec.md) | Disclaimer + AI-disclosure + positioning copy (in-product) |
| LEGAL-002 | MUST | P1 | 12 | AUTH-001 | [TASK-LEGAL-002](TASK-LEGAL-002-pdpd-gdpr/spec.md) | PDPD/GDPR compliance pack (consent, retention, erasure/export contracts) |
| LEGAL-003 | MUST | P1 | 8 | RAG-003 | [TASK-LEGAL-003](TASK-LEGAL-003-ethical-ai/spec.md) | Ethical-AI + cultural-sensitivity guardrails (language rules, school fairness, attribution) |
| LEGAL-004 | MUST | P1 | 4 | LEGAL-001 | [TASK-LEGAL-004](TASK-LEGAL-004-vn-legal-review/spec.md) | VN legal review checklist + counsel sign-off gate (pre-launch) |

One P0 task is authored: LEGAL-001, the in-product disclaimer + AI-disclosure copy + positioning language rules. Three are authored: LEGAL-002 (the PDPD/GDPR compliance pack - consent, retention, and the erasure/export contracts, P1, on AUTH-001), LEGAL-003 (ethical-AI + cultural-sensitivity guardrails - language rules, school fairness, attribution, P1, extending the RAG-003 framing guard), and LEGAL-004 (the VN legal review checklist and counsel sign-off gate before launch, P1, gating LEGAL-001's statute references and wording).

## Internal spine

```
WEB-001 -> LEGAL-001 (in-product disclaimer + AI-disclosure copy + positioning rules)
   -> LEGAL-004 (VN legal review checklist + counsel sign-off gate; pre-launch)
AUTH-001 -> LEGAL-002 (PDPD/GDPR: consent, retention, erasure/export contracts)
RAG-003  -> LEGAL-003 (ethical-AI + cultural-sensitivity guardrails)
```

LEGAL-001 sets the positioning and copy the rest of the product renders; LEGAL-004 gates launch on counsel review of that positioning and the named statutes.

## Cross-module dependencies

- Depends on WEB: LEGAL-001's disclaimer fills the TASK-WEB-001 shell slot and its AI-limits copy is what the `AIDisclosureBadge` popover shows (legal owns the words by key, the component owns the affordance). Depends on AUTH: LEGAL-002's erasure/export contracts operate on TASK-AUTH-001 user data and the TASK-PLAT-003 schema (soft-delete supports it). Depends on RAG: LEGAL-003 extends the TASK-RAG-003 framing guard (no interpretation asserts a certain future or gives medical/legal/financial advice).
- Blocks launch: LEGAL-004 is the pre-launch counsel sign-off gate; the named VN statutes and the final disclaimer wording are informational until it records sign-off.
- Consumed across the product: the positioning rules (LEGAL-001) and the ethical/cultural rules (LEGAL-003) apply to every user-facing task (WEB, CHART, RAG, REPORT, EDU), which inherit the heritage-education framing (strategy 7).

## Module notes

- Heritage-education positioning is product-defining (RISK-4): the product is framed as cultural heritage and decision support, never fortune-telling or destiny prediction, and the language avoids asserting certain future events, avoids medical/legal/financial advice under a divination guise, and avoids fear or dependency (strategy 7). The disclaimer is in-product at the point of use (query + results), never buried in a terms page. This framing is a controlled, versioned artifact (the LEGAL-001 copy deck), so the words are deliberate and consistent, and it is enforceable via a do/don't lexicon the RAG framing guard and a copy-policy check test against.
- The named VN statutes require counsel review before launch (LEGAL-004): Nghi dinh 38/2021/ND-CP (administrative penalties in culture/advertising, including superstition), Dieu 320 Bo luat Hinh su (practicing superstition for profit), and Quyet dinh 34/2020/QD-TTg (sector list/management context) are informational context, not legal conclusions. LEGAL-001 carries them as review input marked `counsel_review: pending`; LEGAL-004 is the sign-off gate, and launch (including app-store submission) is blocked until it is green (RISK-4).
- Citation, AIDisclosure, and HumanReviewGate are the cultural-fairness expression: presenting schools fairly (the engine flag discipline is the technical form of this), citing classical text with the original Han alongside transliteration and translation, labeling every AI output as AI-generated and grounded, and putting a human in the loop for consequential readings are the same respect-and-accountability principle seen from the interface (strategy 4.4, 7). LEGAL-003 makes the language and attribution rules explicit; the RAG citation-required guard, the `AIDisclosureBadge`, and the `HumanReviewGate` are where they are enforced and shown.
- Personal data is sensitive (RISK-5): LEGAL-002 owns the PDPD/GDPR pack - consent, retention, and the erasure/export (DSAR) contracts - which operate on the encrypted birth-data and question-text the platform holds; the data-tier support (soft-delete, audit) is TASK-PLAT-003 and the encryption is TASK-AUTH-001.
