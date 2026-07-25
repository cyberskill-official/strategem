# Classical corpus sources (TASK-KB-003)

Rights and provenance for classical text units. This file is a **schema stub** —
fill rows as corpus is ingested. Do not invent copyright conclusions.

| Field | Meaning |
|---|---|
| `source_id` | Stable id used in citations / RAG |
| `system` | `qimen` / `liuren` / `taiyi` / … |
| `work_title` | Traditional / modern title as known |
| `edition_or_witness` | Edition, manuscript, or digital witness (if known) |
| `rights_status` | `unknown` / `public_domain_claim` / `licensed` / `all_rights_reserved` / `needs_review` |
| `rights_note` | Short factual note only (no legal conclusion) |
| `review_owner` | Who must confirm before commercial use |
| `citation_prefix` | Prefix for unit citation ids |

## Seed inventory (incomplete)

| source_id | system | work_title | edition_or_witness | rights_status | rights_note | review_owner | citation_prefix |
|---|---|---|---|---|---|---|---|
| yen_ba_dieu_tau_ca | qimen | 煙波釣叟歌 / Yên Ba Điếu Tẩu Ca | sample seed for RAG path | needs_review | sample only — not a rights determination | legal HITL | yba_ |

Citation IDs use `citation_prefix` + local slug. Units carry three layers: `nguyen_van_han` / `bach_thoai` / `dich`.
