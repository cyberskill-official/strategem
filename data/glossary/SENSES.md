# Classical term sense layers (TASK-RAG-005)

| Layer | Han | Role | Default |
|---|---|---|---|
| `ban_nghia` | 本義 | base / original sense | on, highest weight |
| `dan_than` | 引申 | extended sense | on |
| `gia_ta` | 假借 | phonetic loan (unrelated meaning) | **off** unless `reliable=true` |
| `dien_tich` | 典故 | allusion | on, lowest weight among defaults |

Expansion is query-side only: it widens retrieval, never asserts meaning.
