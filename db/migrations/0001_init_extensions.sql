-- TASK-PLAT-003: extensions required by the data-tier schema.
-- pgcrypto: gen_random_uuid()
-- citext: case-insensitive email uniqueness
-- pgvector: reserved for TASK-RAG-001 embeddings (no tables here)

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;
-- Optional: uncomment when RAG-001 lands and the image includes pgvector.
-- CREATE EXTENSION IF NOT EXISTS vector;
