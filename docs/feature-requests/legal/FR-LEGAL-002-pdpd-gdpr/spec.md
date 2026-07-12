---
id: FR-LEGAL-002
title: "PDPD/GDPR compliance pack - consent capture at signup, a retention schedule per data class, and the right-to-erasure + data-export contracts AUTH-004 implements (crypto-shred for erasure); birth data and question text classified as sensitive personal data"
module: LEGAL
priority: MUST
status: reviewing
phase: P1
slice: 1
lang: python/doc
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.4, strategy 7, strategy RISK-5, Claude-07 s4.2, Grok-25]
related_frs: [FR-AUTH-001, FR-AUTH-004, FR-PLAT-003, FR-API-004, FR-LEGAL-001, FR-LEGAL-004]
depends_on: [FR-AUTH-001]
blocks: [FR-AUTH-004]
new_paths:
  - docs/legal/pdpd-gdpr/compliance-pack.md
  - docs/legal/pdpd-gdpr/retention-schedule.md
  - docs/legal/pdpd-gdpr/consent.md
  - docs/contracts/dsar.schema.json
  - packages/tamthuc_compliance/__init__.py
  - packages/tamthuc_compliance/dsar.py
  - packages/tamthuc_compliance/retention.py
  - packages/tamthuc_compliance/tests/test_dsar.py
---

## §1 - Description (BCP-14 normative)

This FR defines the data-protection compliance pack: consent capture at signup, a retention schedule per data class, and the right-to-erasure and data-export contracts that FR-AUTH-004 (DSAR self-service) implements. Its legal basis is the Vietnamese PDPD (Nghi dinh 13/2023/ND-CP on personal data protection) and the GDPR (strategy 4.4, RISK-5). It is a python/doc FR: it owns the contracts, the schedule, and the consent copy as reviewable artifacts; it does NOT implement the DSAR runtime endpoints (FR-AUTH-004) nor the encryption at rest (FR-AUTH-001).

Birth data (ngay sinh, gio sinh, kinh do) and question text (cau hoi / free-text loai_cau_hoi) SHALL be classified as sensitive personal data. Consent SHALL be captured at signup: purpose-specific, granular, revocable, and stored with a consent version and timestamp. A retention schedule SHALL define, per data class (birth data, question text, charts, reports, audit), the contents, the lawful basis, the retention period, and the erasure mechanism. The right-to-erasure contract SHALL specify crypto-shred for encrypted sensitive data - destroy the per-record AES-256 key so the ciphertext is unrecoverable - plus row deletion or anonymization for derived data; audit rows SHALL be erasure-exempt and retained per their basis. The data-export contract SHALL produce a machine-readable bundle of all personal data held for a subject. Sensitive data MUST NOT be written to logs (strategy 4.4).

This FR provides the contract and the schedule; FR-AUTH-004 implements the export and erasure endpoints against them, and the named statutes and final wording are reviewed at FR-LEGAL-004 before launch.

## §2 - Why this design (rationale for humans)

The personal data here is unusually sensitive: a person's birth data plus the question they bring to a divination-adjacent product (RISK-5). Two regimes apply - the VN PDPD (Nghi dinh 13/2023/ND-CP) for Vietnamese users and the GDPR for EU users - so the pack is written to the stricter of the two per requirement, and one implementation satisfies both rather than two half-built ones.

Owning the erasure and export contracts here, not inside FR-AUTH-004, means the legal requirement and the engineering interface are one reviewed artifact: AUTH-004 implements an interface legal has signed off, not its own reading of the law. Crypto-shred is the erasure mechanism precisely because the sensitive fields are AES-256 encrypted at rest (FR-AUTH-001): destroying the key, not chasing every copy of the ciphertext, is what makes erasure actually complete across replicas and backups. The audit exemption is deliberate and lawful - erasing the audit trail would defeat the accountability the audit exists for, and both PDPD and GDPR permit retention for a legal or security obligation. Classifying birth data and question text as sensitive up front, and making the schedule the single source every store maps to, is what stops a new table from quietly holding sensitive data with no retention rule.

## §3 - Contract (schedule / consent / DSAR contracts)

### Data classification and retention schedule (`retention-schedule.md`, `retention.py`)

| Data class | Contents | Sensitive | Lawful basis | Retention | Erasure |
|---|---|---|---|---|---|
| birth_data | ngay sinh, gio sinh, kinh do (dau_vao) | yes | consent | while account active | crypto-shred (destroy AES-256 key) |
| question_text | cau hoi / free-text loai_cau_hoi | yes | consent | while account active | crypto-shred / delete |
| charts | la so envelopes (reproducible from dau_vao) | derived | contract | while account active | delete row |
| reports | StructuredReport artifacts | derived | contract | while account active | delete row |
| audit | sensitive-action audit rows | operational record | legal obligation / legitimate interest | 12-24 months minimum | retained (erasure-exempt) |

`retention.py` exposes the schedule as typed data so FR-AUTH-004 and FR-PLAT-003 read one source, not two copies.

### Consent capture (`consent.md`)

Consent is captured at signup: granular per purpose, revocable, stored with `consent_version` + timestamp + scope, with a withdrawal path. User-facing consent copy is keyed via FR-LEGAL-001 `copy-keys.yaml`, never inlined.

### DSAR contracts (`dsar.py` + `docs/contracts/dsar.schema.json`)

```python
from typing import Protocol
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class DataClass(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str                          # birth_data | question_text | charts | reports | audit
    sensitive: bool
    lawful_basis: str                  # consent | contract | legal_obligation | legitimate_interest
    retention: str                     # "account_active" | ISO 8601 duration | "12m..24m"
    erasure: str                       # crypto_shred | delete | anonymize | retained

class ExportBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject_id: UUID
    generated_at: datetime
    records: dict                      # per data class -> the subject's data, decrypted for the subject only

class ErasureReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject_id: UUID
    erased_at: datetime
    crypto_shredded: list[str]         # data classes whose keys were destroyed
    deleted: list[str]
    retained: list[str]                # e.g. ["audit"] with the retaining basis

class ExportContract(Protocol):
    def export(self, subject_id: UUID) -> ExportBundle: ...

class ErasureContract(Protocol):
    def erase(self, subject_id: UUID) -> ErasureReceipt: ...   # crypto-shred sensitive, preserve audit; idempotent
```

FR-AUTH-004 implements `ExportContract` and `ErasureContract`; this FR owns their shape and the JSON Schema. `erase` is idempotent: a second call returns the same receipt shape and changes nothing.

## §4 - Acceptance criteria

1. The retention schedule (doc + `retention.py`) defines every data class - birth data, question text, charts, reports, audit - with contents, sensitivity, lawful basis, retention, and erasure mechanism; birth data and question text are marked sensitive.
2. The DSAR contracts (`ExportContract`, `ErasureContract`) exist as typed interfaces plus a JSON Schema; a conformance test asserts the shape FR-AUTH-004 must implement.
3. The erasure contract specifies crypto-shred for sensitive encrypted classes and retains audit rows (erasure-exempt); `erase` is idempotent.
4. Consent capture is specified as granular, revocable, and versioned + timestamped at signup.
5. The legal basis is documented as Nghi dinh 13/2023/ND-CP (VN PDPD) + GDPR, meeting the stricter per requirement.
6. No sensitive data appears in logs (the pack states the rule; a check aligns with the PLAT logging config).

## §5 - Verification

- `test_dsar.py` with a fake store implementing the contracts: `export` returns a bundle covering every non-retained class; `erase` crypto-shreds the sensitive classes, deletes the derived rows, and retains audit; a second `erase` is a no-op with the same receipt shape (idempotent).
- Schema: `docs/contracts/dsar.schema.json` validates `ExportBundle` + `ErasureReceipt`; Pydantic and JSON Schema parity is checked in CI.
- Retention completeness: a test asserts every FR-PLAT-003 table holding personal data maps to a data class in the schedule (no unclassified sensitive store).
- Doc review: the pack is marked for counsel review at FR-LEGAL-004.
- Gates: `ruff check`, `mypy tamthuc_compliance`, `python -m pytest packages/tamthuc_compliance`.

## §6 - Implementation skeleton

1. `retention-schedule.md`: the classification table + the PDPD/GDPR basis.
2. `retention.py`: the schedule as typed data (`DataClass` list) that AUTH-004 and PLAT-003 read.
3. `consent.md`: consent capture spec (granular, revocable, versioned); copy keyed via FR-LEGAL-001.
4. `dsar.py` + `docs/contracts/dsar.schema.json`: `ExportContract`, `ErasureContract`, `ExportBundle`, `ErasureReceipt`.
5. `tests/test_dsar.py`: fake store, export/erase/idempotency, retention-completeness.
6. Hand the statute mapping to FR-LEGAL-004; mark the pack `counsel_review: pending`.

## §7 - Dependencies

Depends on FR-AUTH-001 (birth-data AES-256 encryption + profile; crypto-shred destroys the keys AUTH-001 manages). Blocks FR-AUTH-004 (DSAR self-service implements the export and erasure contracts). Aligns with FR-PLAT-003 (the tables the schedule classifies and the audit rows it exempts) and FR-API-004 (persistence + audit rows). User-facing consent copy is keyed via FR-LEGAL-001; the statutes and final wording are reviewed at FR-LEGAL-004.

## §8 - Example payloads

```json
// ErasureReceipt - what AUTH-004 returns after a DSAR erasure
{ "subject_id": "a0f1...", "erased_at": "2026-07-08T12:00:00Z",
  "crypto_shredded": ["birth_data", "question_text"],
  "deleted": ["charts", "reports"],
  "retained": ["audit"] }

// a retention-schedule row as typed data
{ "name": "birth_data", "sensitive": true, "lawful_basis": "consent",
  "retention": "account_active", "erasure": "crypto_shred" }
```

## §9 - Open questions

- Retention of question text after account closure vs while active. Default: erase on account deletion / DSAR; if a shorter active-life TTL is wanted, set it in the schedule (one place).
- Audit retention duration (12 vs 24 months). Default: 12 months minimum, extend per statute; counsel confirms at FR-LEGAL-004.
- Whether charts / reports are erased or kept as anonymized aggregates. Default: delete on erasure (they are reproducible and tied to sensitive input); no anonymized retention at MVP.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Sensitive data logged | a log line prints birth data / question text | forbidden (strategy 4.4); redaction; a log check |
| Incomplete erasure | a replica / backup keeps recoverable ciphertext | crypto-shred destroys the key so ciphertext is unrecoverable everywhere; receipt lists shredded classes |
| Audit erased | erase deletes audit rows | forbidden; audit is erasure-exempt (legal basis); a test asserts audit retained |
| Unclassified sensitive store | a new table holds birth / question data with no schedule entry | retention-completeness test fails |
| Consent missing / stale | signup without recorded consent | blocked; consent captured + versioned at signup |
| Contract drift | AUTH-004 diverges from the contract | schema + conformance test |

## §11 - Notes

Package `tamthuc_compliance` (Python, DEC-2). This is the RISK-5 mitigation as a reviewable artifact: two regimes (VN PDPD Nghi dinh 13/2023/ND-CP + GDPR) met as one pack at the stricter bar. Crypto-shred is the erasure mechanism that is actually complete across backups, because the AES-256 key - not the ciphertext - is the thing destroyed (FR-AUTH-001 owns the keys). LEGAL owns the contract and the schedule; FR-AUTH-004 implements the endpoints against them; the audit exemption is deliberate and lawful. Reviewed at FR-LEGAL-004 before launch. refs Claude-07 s4.2, Grok-25.
