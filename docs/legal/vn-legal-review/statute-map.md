# Statute map (TASK-LEGAL-004)

Maps the named Vietnamese statutes (informational context from Claude-07 s4.2 /
strategy RISK-4) to the product surfaces counsel must review before public
launch or app-store submission. **This document is not legal advice.**

| Statute | Concerns | Product surface to verify |
|---|---|---|
| Nghị định 38/2021/NĐ-CP | Administrative penalties in culture / advertising, including superstition | Marketing and ad copy; home / pricing positioning; in-product disclaimer (LEGAL-001); follow-up chat framing; store listing drafts |
| Điều 320 Bộ luật Hình sự | Crime of practicing superstition for profit | Core framing (heritage education / decision support, not fortune-telling); paywall / pricing language; no fear or dependency copy (LEGAL-003); AI disclosure limits; monetized interpretation |
| Quyết định 34/2020/QĐ-TTg | Sector list and management context | Business scope / registration classification; how the product is described publicly and to app stores |

## Related compliance surfaces (reviewed with LEGAL-002 / LEGAL-003)

| Instrument / rule | Concerns | Product surface |
|---|---|---|
| Nghị định 13/2023/NĐ-CP (PDPD) + GDPR | Personal data, consent, retention, DSAR | `docs/legal/pdpd-gdpr/`; birth data; query text; export / erasure |
| Ethical-AI language rules (Claude-07 s4.1) | Certain-future, medical/legal/financial advice, fear/dependency | RAG + follow-up output; lexicon |
| School fairness (Claude-07 / strategy 4.4) | One-school absolutism | `co_truong_phai` stamps; interpretation prose |
| Source attribution (Claude-07 s4.3) | Cite classical text; Han + transliteration + dich | Citation cards; knowledge / results UI |
| App-store divination policies | Listing rejection / removal | Apple / Google listing copy (checklist item 15) |

Related owner tasks: LEGAL-001 (copy deck), LEGAL-002 (PDPD/GDPR pack), LEGAL-003
(ethical-AI), WEB-002/003 (disclaimer at point of use), WEB-006/008 (i18n).
