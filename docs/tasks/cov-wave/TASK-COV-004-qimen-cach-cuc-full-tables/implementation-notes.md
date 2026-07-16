# COV-004 implementation notes

## Landed

| artefact | path |
|----------|------|
| Pattern catalog (≥40) | `crates/cyberos-qimen/patterns/qimen_cach_cuc.json` |
| Detection from catalog | `crates/cyberos-qimen/src/cach_cuc.rs` (`pattern_catalog()`, `match_ordered`) |
| Catalog + detection tests | `crates/cyberos-qimen/tests/cov004_pattern_catalog.rs` |
| Vernacular UI map | `apps/web/src/lib/domain/glossary.ts` |
| Web smoke | `apps/web/tests/pattern-vernacular-cov004.test.mjs` |

## §1 AC

1. ≥40 named patterns with conditions (sky/earth) + citations — **yes** (47 rows)
2. ≥15 high-priority detections on goldens — **yes** (15 curated ids)
3. No polarity without rule match — **yes** (am empty; match only catalog)
4. Vernacular names first in web — **yes** (`displayPatternName` + expanded PATTERN table)

## Tests

`cargo test -p cyberos-qimen --test cov004_pattern_catalog --test cach_cuc_oracle` green.  
Evidence: `{SCRATCH}/cov004-tests.log`.

## Status

`ready_to_review` — **HITL required**. Agent will not set `done`.
