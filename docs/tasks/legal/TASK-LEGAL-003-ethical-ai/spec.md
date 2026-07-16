---
id: TASK-LEGAL-003
title: "Ethical-AI + cultural-sensitivity guardrails - the language do/don't rules, school fairness (the co_truong_phai flag discipline as its technical form), and source attribution (Han beside transliteration and translation); enforced as content rules plus automated checks over RAG-003 output"
module: LEGAL
priority: MUST
status: done
phase: P1
slice: 1
lang: doc/python
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 7, strategy RISK-4, Claude-07 s4.1, Claude-07 s4.3, Claude-07 s2.3]
related_frs: [TASK-RAG-003, TASK-LEGAL-001, TASK-LEGAL-004, TASK-PLAT-002, TASK-KB-003, TASK-WEB-003]
depends_on: [TASK-RAG-003]
blocks: []
new_paths:
  - docs/legal/ethical-ai/ethical-ai-rules.md
  - docs/legal/ethical-ai/school-fairness.md
  - docs/legal/ethical-ai/source-attribution.md
  - docs/legal/tests/ethics-checks.md
  - packages/tamthuc_rag/tamthuc_rag/ethics.py
  - packages/tamthuc_rag/tests/test_ethics.py
---

## §1 - Description (BCP-14 normative)

This task defines the ethical-AI and cultural-sensitivity guardrails and enforces them as content rules plus automated checks over the TASK-RAG-003 interpretation output (Claude-07 s4.1, s4.3; strategy 7). It has three rule families.

Language do/don't: an interpretation SHALL NEVER assert a certain future event; SHALL NEVER give medical, legal, or financial advice under a divination guise; and SHALL NEVER induce fear or dependency. These extend the TASK-LEGAL-001 do/don't lexicon and restate it for AI output. School fairness: schools SHALL be presented evenhandedly; no interpretation SHALL claim one school is uniquely or absolutely correct; the co_truong_phai (school-flag) discipline of TASK-PLAT-002 is the technical form of this fairness - a chart stamps the school it used rather than hardcoding one as truth (strategy 4.4, RISK-2). Source attribution: every interpretive claim SHALL cite classical text, and a citation SHALL keep the original Han beside its transliteration (phien am / bach thoai) and its translation (dich) - the three-layer citation card (TASK-KB-003, TASK-WEB-003).

The rules SHALL be enforced by `ethics.py` over a RAG-003 `Interpretation`, extending the RAG-003 framing guard; a high-severity finding blocks and a lower-severity finding routes to the HumanReviewGate (TASK-RAG-004). This task depends on TASK-RAG-003, aligns its language rules with TASK-LEGAL-001, and is reviewed at TASK-LEGAL-004.

## §2 - Why this design (rationale for humans)

The risk here is linguistic and cultural, not computational (strategy 7, RISK-4). The language rules are the ethical floor that keeps the product on the heritage-education side of VN law; TASK-LEGAL-001 owns the words and TASK-RAG-003 has a framing guard, so this task's job is to make the enforcement a named, testable content-rule layer that nothing consequential can bypass on editorial intent alone.

School fairness matters because Tam Thuc has real school disagreements; asserting one school as the single truth is both a scholarship error and a disrespect, and it alienates half the users (RISK-2). The technical expression of fairness already lives in the architecture - co_truong_phai stamps the school a chart used rather than hardcoding one (strategy 4.4) - so this task keeps the interpretation prose consistent with that: describe under which convention a reading holds, do not crown a winner. Source attribution unifies the technical citation-required rule (Claude-06) with the cultural respect-the-source rule (Claude-07 s4.3): they are one rule. Keeping the Han beside transliteration and translation lets a user reach the primary source, which is both honest and higher quality. Placing the checker in the RAG package, over the same `Interpretation` object the framing guard sees, is what makes these rules run on every AI output rather than living only in a document.

## §3 - Contract (rules and checks)

### Language do/don't (`ethical-ai-rules.md`)

Extends the TASK-LEGAL-001 `lexicon-do-dont.md`, restated for AI output. Four forbidden categories:

| Category | Forbidden | Heritage / decision-support instead |
|---|---|---|
| certain-future | "you will ...", "is destined / guaranteed" | "the reading suggests a supportive window ..." |
| medical | "cure", "diagnosis", "you have <condition>" | "for planning and reflection" |
| legal / financial | "you should sue / sign / invest in ..." | "as one input to your own decision" |
| fear / dependency | "consult daily or misfortune follows" | "a heritage practice to explore" |

### School fairness (`school-fairness.md`)

Present schools evenhandedly; state the convention (co_truong_phai) a reading used; never assert a school is uniquely correct; when schools diverge, name the divergence rather than hide it. The co_truong_phai flag discipline (TASK-PLAT-002) is the technical form of this rule.

### Source attribution (`source-attribution.md`)

Every claim cites classical text; each `CitationCard` keeps `han` + `bach_thoai` (phien am) + `dich` + `locator`; a claim whose card drops the Han where the source unit has Han is a defect (three-layer card, Claude-07 s4.3).

### Automated checks (`ethics.py`)

```python
from pydantic import BaseModel, ConfigDict

class EthicsFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: str            # language | school_fairness | attribution
    severity: str            # high (block) | medium (route to HumanReviewGate)
    span: str                # the offending text or citation_id
    rule: str                # which rule fired

def check_ethics(interp: "Interpretation") -> list[EthicsFinding]:
    # (a) language: forbidden lexicon (certain-future / medical / legal-financial / fear-dependency)
    #     over beginner + expert + recommendations; reuse the TASK-LEGAL-001 copy-policy lexicon
    # (b) school fairness: flag absolutist one-school claims; require convention (co_truong_phai) framing
    # (c) attribution: every claim cited; each card has han + transliteration + dich where the source provides them
    ...
```

Policy (`ethics-checks.md`): high-severity findings (advice verdict, certain-future) block the output; medium-severity findings (fairness, attribution, fear/dependency) route to the TASK-RAG-004 HumanReviewGate.

## §4 - Acceptance criteria

1. The three rule docs exist: language do/don't (extending TASK-LEGAL-001), school fairness (naming co_truong_phai as the technical form), and source attribution (Han beside transliteration + translation).
2. `check_ethics` runs over a RAG-003 `Interpretation` and returns findings per family; a clean output yields no findings.
3. Language check: a certain-future / medical / legal-financial / fear-dependency phrasing is flagged, aligned with the TASK-LEGAL-001 copy-policy and the RAG-003 framing guard.
4. School-fairness check: an absolutist one-school claim is flagged; a reading that states its convention is not.
5. Attribution check: a claim whose citation card lacks the Han where the source has Han, or lacks a citation, is flagged.
6. Policy: high-severity findings block; medium-severity route to the HumanReviewGate; a test covers both paths.

## §5 - Verification

- `test_ethics.py`: canned `Interpretation`s (clean, certain-future, advice-verdict, one-school-absolutist, missing-Han citation, uncited claim); assert the right category, severity, and routing for each.
- Alignment: the language check shares the TASK-LEGAL-001 forbidden-lexicon spec (one source of forbidden phrasing); a test asserts parity with the RAG-003 framing-guard policy set.
- Attribution: a citation card missing `han` while its source unit has Han fails; the three-layer card shape is checked against TASK-KB-003.
- Path test: the RAG-003 / HumanReviewGate flow invokes `check_ethics` (a spy asserts the check is not bypassed).
- Gates: `ruff check`, `mypy tamthuc_rag`, `python -m pytest packages/tamthuc_rag`.

## §6 - Implementation skeleton

1. `ethical-ai-rules.md`: the four forbidden categories restated for AI output; reference TASK-LEGAL-001.
2. `school-fairness.md`: the evenhandedness rules; co_truong_phai as the technical form (TASK-PLAT-002).
3. `source-attribution.md`: cite classical text; Han beside transliteration + dich; the card shape.
4. `ethics.py`: `check_ethics` with the three families + `EthicsFinding`; reuse the copy-policy lexicon.
5. `ethics-checks.md`: how RAG-003 / HumanReviewGate invoke the checks and the block-vs-route policy.
6. `tests/test_ethics.py`: the canned-`Interpretation` matrix.

## §7 - Dependencies

Depends on TASK-RAG-003 (the `Interpretation` output the checks run over; extends its framing guard). Extends TASK-LEGAL-001 (the forbidden-lexicon copy-policy and positioning rules). Reads the TASK-PLAT-002 co_truong_phai discipline as the technical form of school fairness. Aligns with TASK-KB-003 and TASK-WEB-003 (the three-layer citation card the attribution rule checks). Reviewed at TASK-LEGAL-004. Nothing hard-depends on this task (blocks empty); it is an enforcement layer the RAG path and the review gate call.

## §8 - Example payloads

```json
// check_ethics output on an interpretation with a verdict and a one-school claim
[
  { "category": "language", "severity": "high",
    "span": "you will certainly close the deal", "rule": "certain-future assertion" },
  { "category": "school_fairness", "severity": "medium",
    "span": "only the chaibu school is correct", "rule": "one-school absolutism" },
  { "category": "attribution", "severity": "medium",
    "span": "yba_dieu_012", "rule": "citation card missing han" }
]
```

## §9 - Open questions

- Block vs route threshold per category. Default: certain-future and advice-verdict block; fear/dependency, fairness, and attribution route to the HumanReviewGate; tune from review outcomes.
- School-fairness detection is heuristic (absolutist phrasing). Default: a conservative lexicon of one-school-absolutist markers plus review; not a semantic judge at MVP.
- Whether attribution requires Han for sources with no Han original (e.g. a modern VN commentary). Default: require Han only where the source unit provides it; transliteration + dich always.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Certain-future / advice verdict | interpretation asserts a fixed future or a medical/legal/financial ruling | high-severity, blocked (strategy 7, TASK-LEGAL-001) |
| One-school absolutism | claims a school is uniquely correct | flagged; require convention (co_truong_phai) framing (RISK-2) |
| Missing Han | citation card drops the original Han | flagged; three-layer card required (Claude-07 s4.3) |
| Uncited claim | a claim with no citation | flagged (defense in depth with TASK-RAG-003) |
| Fear / dependency | prose induces reliance or dread | flagged; ethical floor |
| Checks bypassed | the RAG path skips `ethics.py` | wired into RAG-003 / HumanReviewGate; a path test asserts invocation |

## §11 - Notes

Package hook in `tamthuc_rag` (Python, DEC-2). This task is the cultural-and-ethical layer stated as content rules plus automated checks, sitting on top of the RAG-003 framing guard and the TASK-LEGAL-001 lexicon. Its throughline is that respect-the-source and cite-the-source are one rule (Claude-07 s4.3): the Han beside transliteration and translation is both scholarship and honesty. School fairness is not a slogan but the co_truong_phai flag discipline seen in prose (strategy 4.4, RISK-2). Reviewed at TASK-LEGAL-004 before launch. refs Claude-07 s4.1, s4.3, s2.3.
