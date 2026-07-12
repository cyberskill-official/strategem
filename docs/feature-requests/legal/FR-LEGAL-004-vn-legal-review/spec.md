---
id: FR-LEGAL-004
title: "VN legal review checklist + counsel sign-off gate - the named statutes (Nghi dinh 38/2021/ND-CP, Dieu 320 Bo luat Hinh su, Quyet dinh 34/2020/QD-TTg), a pre-launch checklist, and a HARD counsel sign-off gate before public launch and app-store submission (RISK-4)"
module: LEGAL
priority: MUST
status: done
phase: P1
slice: 1
lang: doc
effort_h: 4
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 7, strategy RISK-4, Claude-07 s4.2]
related_frs: [FR-LEGAL-001, FR-LEGAL-002, FR-LEGAL-003, FR-WEB-001, FR-WEB-002, FR-WEB-003]
depends_on: [FR-LEGAL-001]
blocks: []
new_paths:
  - docs/legal/vn-legal-review/checklist.md
  - docs/legal/vn-legal-review/statute-map.md
  - docs/legal/vn-legal-review/sign-off-gate.md
  - docs/legal/vn-legal-review/counsel-signoff-record.md
---

## §1 - Description (BCP-14 normative)

This FR is the pre-launch legal review: a checklist, a map of the named Vietnamese statutes to the product surfaces they touch, and a HARD counsel sign-off gate. The named statutes SHALL be Nghi dinh 38/2021/ND-CP (administrative penalties in culture and advertising, including superstition), Dieu 320 Bo luat Hinh su (the crime of practicing superstition for profit), and Quyet dinh 34/2020/QD-TTg (sector list and management context) (Claude-07 s4.2, strategy 7).

Counsel sign-off SHALL be a HARD gate: public launch and app-store submission SHALL NOT proceed while sign-off is pending (RISK-4). The checklist SHALL cover the positioning (heritage education, not fortune-telling), the disclaimer placement (FR-LEGAL-001), the ethical-AI rules (FR-LEGAL-003), the data-protection pack (FR-LEGAL-002), and the advertising / marketing copy. The sign-off record SHALL name the reviewer, date, scope, statutes reviewed, verdict, any conditions, and a re-review trigger, and SHALL flip the FR-LEGAL-001 `counsel_review` marker from pending to approved only via a recorded sign-off. This is a document and release-process FR; it does not change product code - it gates the release of it. It depends on FR-LEGAL-001, whose deck carries `counsel_review: pending` until this gate records sign-off.

## §2 - Why this design (rationale for humans)

RISK-4 is the highest legal exposure in the project. Under VN law the line between a heritage-education tool and superstition-for-profit carries administrative and even criminal exposure (Dieu 320 Bo luat Hinh su), and no amount of careful copy substitutes for a Vietnamese lawyer reviewing the actual shipped features (Claude-07 s4.2 is explicit that its statute list is informational and requires counsel review before launch).

Making sign-off a hard gate - not a checkbox someone can skip under launch pressure - is the whole point. The checklist and the statute map exist so counsel reviews against a concrete surface rather than an abstract idea, and the sign-off record is the artifact that says the gate was actually passed, by whom, and for what scope. App-store submission is called out separately because the stores add their own policy surface on divination and fortune-telling content, and a rejected or pulled listing is its own harm. This FR is deliberately small in hours because its value is procedural, not technical: it wires the public launch of the product to a human legal decision, and it re-opens on any material change so an old approval cannot cover a new surface.

## §3 - Contract (statute map / checklist / gate / record)

### Statute map (`statute-map.md`)

| Statute | Concerns | Product surface to verify |
|---|---|---|
| Nghi dinh 38/2021/ND-CP | administrative penalties in culture / advertising, incl. superstition | marketing and ad copy, positioning, disclaimer (FR-LEGAL-001) |
| Dieu 320 Bo luat Hinh su | crime of practicing superstition for profit | the core framing (decision support, not fortune-telling), paywall / pricing language, no fear or dependency (FR-LEGAL-003) |
| Quyet dinh 34/2020/QD-TTg | sector list and management context | business scope / registration, how the product is classified |

### Pre-launch checklist (`checklist.md`)

Each item names its owner FR: positioning copy in-product (FR-LEGAL-001); disclaimer at the point of use (FR-WEB-002/003); AI-limits copy keyed (FR-LEGAL-001); ethical-AI checks active over RAG output (FR-LEGAL-003); data-protection pack + consent + DSAR contracts (FR-LEGAL-002); marketing / ad copy reviewed against Nghi dinh 38; no certain-future / fear / dependency phrasing anywhere; app-store listing copy reviewed.

### Sign-off gate (`sign-off-gate.md`)

Launch and app-store submission are blocked until counsel records sign-off in `counsel-signoff-record.md`. The FR-LEGAL-001 deck's `counsel_review` marker moves to approved only via that record. A conditional sign-off lists conditions that MUST be closed before launch.

### Sign-off record (`counsel-signoff-record.md`)

Fields: reviewer (name, bar / firm), date, scope reviewed, statutes reviewed, verdict (approved | approved-with-conditions | rejected), conditions, and re-review trigger (a material feature change touching positioning, monetization, or data handling).

## §4 - Acceptance criteria

1. `statute-map.md` names all three statutes and maps each to the product surface it touches.
2. `checklist.md` is a complete pre-launch list, each item pointing at its owner FR (LEGAL-001/002/003, WEB-002/003).
3. `sign-off-gate.md` defines the hard gate: no public launch and no app-store submission while sign-off is pending.
4. `counsel-signoff-record.md` is a record template with reviewer, date, scope, statutes, verdict, conditions, and re-review trigger.
5. The gate flips the FR-LEGAL-001 `counsel_review` marker from pending to approved only via a recorded sign-off; a conditional sign-off enumerates blocking conditions.
6. A material feature change re-opens the gate (the record carries a re-review trigger).

## §5 - Verification

- Traceability: the checklist covers positioning, disclaimer placement, AI limits, ethical-AI, data protection, and advertising copy; every item has an owner FR.
- Gate check (process): the release / app-store step asserts `counsel-signoff-record.md` exists with verdict approved (or approved-with-conditions and all conditions closed); a pending or absent record blocks the release step.
- Consistency: the FR-LEGAL-001 deck's `counsel_review` marker matches the record verdict.
- No code gate here; this is a documentation and release-process FR whose evidence is the checklist, the map, and the recorded sign-off.

## §6 - Implementation skeleton

1. `statute-map.md`: the three statutes mapped to surfaces.
2. `checklist.md`: the pre-launch items with owner FRs.
3. `sign-off-gate.md`: the hard-gate protocol (launch + app-store).
4. `counsel-signoff-record.md`: the record template.
5. Wire the gate into the release checklist and the `PROMPT.md` safety invariants so launch cannot proceed on a pending record.

## §7 - Dependencies

Depends on FR-LEGAL-001 (the positioning / disclaimer deck it reviews and whose `counsel_review` marker it flips). Reviews FR-LEGAL-002 (data-protection pack) and FR-LEGAL-003 (ethical-AI rules) as checklist items, and the FR-WEB-001/002/003 surfaces where the copy renders. Nothing depends on this FR in the catalog (blocks empty), but functionally it gates the public launch of the whole product - the safety invariant "LEGAL-004 counsel sign-off gates launch" (RISK-4).

## §8 - Example payloads

```
# counsel-signoff-record.md (skeleton)
reviewer: <name, bar / firm>
date: <yyyy-mm-dd>
scope: <features and copy reviewed>
statutes_reviewed: [Nghi dinh 38/2021/ND-CP, Dieu 320 Bo luat Hinh su, Quyet dinh 34/2020/QD-TTg]
verdict: approved | approved-with-conditions | rejected
conditions: [ ... must be closed before launch ... ]
re_review_trigger: material change to positioning / monetization / data handling
```

## §9 - Open questions

- In-house vs external counsel. Default: external Vietnamese counsel for the first sign-off (specialist in culture / advertising law); Stephen procures.
- App-store specifics (Apple / Google divination policy). Default: review each store's policy as a checklist sub-item; the store listing copy is part of scope.
- Re-review cadence. Default: re-review on any material feature change touching positioning, monetization, or data handling, plus an annual refresh.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Launch on pending sign-off | a release proceeds without a recorded approval | blocked; the gate is hard (RISK-4); the release step fails on a pending / absent record |
| App-store submission skips the gate | listing submitted before sign-off | forbidden; app-store submission is in scope of the gate |
| Stale sign-off | product changed materially after approval | the re-review trigger re-opens the gate |
| Checklist item unowned | an item has no owner FR / evidence | traceability check fails |
| Conditional sign-off ignored | launch with open conditions | blocked; all conditions closed before launch |

## §11 - Notes

This is the RISK-4 gate: the smallest FR by hours and one of the most important by consequence. Nothing here is legal advice; it is the process that puts a Vietnamese lawyer between the finished product and the public, reviewing the real shipped surface against Nghi dinh 38/2021/ND-CP, Dieu 320 Bo luat Hinh su, and Quyet dinh 34/2020/QD-TTg (Claude-07 s4.2). The sign-off record is the artifact of record; the hard gate is what keeps it from being skipped under launch pressure. It consumes the FR-LEGAL-001 deck and reviews the FR-LEGAL-002 and FR-LEGAL-003 work as checklist items.
