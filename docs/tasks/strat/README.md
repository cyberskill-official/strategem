# STRAT - strategic tools

Feature requests for the strategic tools: the headline product surface that turns a cast chart into a decision-support instrument. 4 tasks, ~44 engineering-hours, P1-P2. Rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (strategy 5). Primary sources: Claude 07 (strategic use, the chu-khach / dung than decision frame) and Grok 02 (timing and scenario). Language is Python / TS (DEC-2); the compute lives in Python (`tamthuc_strat`), the surfaces in the web app. Implementation order and trigger: `../IMPLEMENTATION_ORDER.md` + `../PROMPT.md`.

STRAT is where the "Strategem" positioning lives. The other modules cast a chart and interpret it; STRAT builds the tools that make that chart actionable for a real decision - scan a date range for good windows, compare options side by side, frame a situation as chu (self) vs khach (other), and cross-check the three engines against one another. Everything here is framed as a structured lens for a decision the user still makes, never a verdict (strategy 7).

## Summary

Four tasks, ~44 engineering-hours. One (STRAT-001, the Timing Optimizer) is authored; the other three are authored. STRAT-001 (scan + score timing windows) is the foundation STRAT-002 (Scenario Comparison) builds on; STRAT-003 (chu-khach decision framework) rides on RAG interpretation; STRAT-004 (cross-system validate) reads two engines and shows their agreement.

## task list

| task | Pri | Phase | h | Title |
|---|---|---|--:|---|
| [STRAT-001](TASK-STRAT-001-timing-optimizer/spec.md) | MUST | P1 | 16 | Timing Optimizer (date-range scan, scored windows) |
| STRAT-002 | SHOULD | P1 | 10 | Scenario Comparison (compare timing results across options) |
| STRAT-003 | SHOULD | P1 | 8 | Chu-khach decision framework (4-step, dung than framing) |
| STRAT-004 | SHOULD | P2 | 10 | Cross-system validate (/calculate/all + agreement view) |

Total: 44h. Only STRAT-001 is authored in full; the rest are authored.

## Cross-module dependencies

- STRAT-001 depends on TASK-QMDG-006 (it casts a QiMen chart for each candidate time via the engine) and TASK-RULE-003 (it selects and weights the cach cuc that matter for the question type). STRAT-002 depends on STRAT-001 (it compares TimingResults across options). STRAT-003 depends on TASK-RAG-003 (the four-step frame is a structured interpretation surface). STRAT-004 depends on TASK-QMDG-006 and TASK-LN-006 (it casts two engines and shows agreement).
- Reads the TASK-PLAT-002 la so envelope throughout; when TASK-QMDG-007 (dung than by question type) lands, the Timing Optimizer's palace filter tightens.
- Blocks / feeds: the STRAT surfaces render in the web app (the Timing Optimizer and Scenario Comparison screens) and feed REPORT; the scored windows and comparisons are report-ready artifacts.

Internal picture: `{QMDG-006, RULE-003} -> STRAT-001 -> STRAT-002`; `RAG-003 -> STRAT-003`; `{QMDG-006, LN-006} -> STRAT-004`.

## Module notes

- Package: `tamthuc_strat` (Python) for the compute; the interactive surfaces are web (TS). STRAT-001 owns the scan-and-score engine.
- The Timing Optimizer is the product's headline strategic tool: it scans candidate times over a date range, casts QiMen for each via the engine, scores each window by its cat / hung cach cuc, and returns the top recommended windows with scores and contributing patterns (Claude-07 s1.1, Grok-02). It scans via the engine and never casts a chart itself; the score is a pure, documented function of the envelope's `cach_cuc`, so every recommendation is explainable and auditable, not a black box.
- All four tools are decision-support framings, never predictions. A scored window, a scenario comparison, or a chu-khach reading is a structured lens the user weighs against real context before deciding (Claude-07 s2). The chu-khach frame (STRAT-003) is the four-step process - name the question and dung than, cast and read the position, check against real context, then the user decides.
- Cross-system validate (STRAT-004) is the technical expression of the tam-tai division of labor: QiMen for direction and timing, LiuRen for the concrete affair, TaiYi for the macro backdrop. It shows where the engines agree and where they diverge, rather than forcing one verdict.
