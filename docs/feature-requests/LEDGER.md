# Tam Thuc Strategem - execution ledger

Append-only. Every task run adds one entry (the agent appends during work; the reviewer appends the verdict). Never edit or delete a past entry; corrections are new entries referencing the old one.

Entry format:

```
## <YYYY-MM-DD> <TASK-ID> <short title> - <agent|operator>
- branch: auto/tt-<id-lowercase>
- commits: <hashes>
- status: <from> -> <to>            # draft->ready_to_implement | ready_to_implement->implementing | implementing->in_review | in_review->done | ->blocked (reason)
- gates: <commands run and results, one line each>     # cargo/ruff/pnpm + oracle diff where relevant
- evidence: <test output refs, oracle-diff numbers, screenshot paths, measured p95, commit hashes>
- sensitive paths: <none | list + justification>       # auth, RLS, birth data, secrets, deploy, envelope contract
- notes: <deviations from the FR spec, discovered follow-ups filed as new tasks, do not scope-creep>
```

Evidence expectations by task class:
- Engines: the oracle-diff result (sample size, mismatch count, which flag combos). CORE additionally the sxwnl term-max-error in seconds and the tyme4py pillar pass/fail.
- Contract (PLAT-002): the cross-language round-trip result and the schema-drift check.
- Data/auth: the no-GUC RLS probe row count (must be zero), proof birth data is encrypted and unlogged.
- Interpretation: citation-resolution check, AIDisclosure present, chart-field-write check (must be none).
- Frontend: screenshot path, diacritics clip-test result, accessibility note.

---

<!-- entries appended below -->
