-- FR-PLAT-003: charts — persisted la so envelopes (FR-PLAT-002) keyed for cache (FR-PLAT-006).

CREATE TABLE charts (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  query_id       uuid NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
  user_id        uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  he             text NOT NULL,       -- luc_nham|ky_mon|thai_at
  envelope       jsonb NOT NULL,      -- the FR-PLAT-002 la so envelope
  cache_key      text NOT NULL,       -- FR-PLAT-002 cache key (FR-PLAT-006 reads it)
  engine_version text NOT NULL,
  created_at     timestamptz NOT NULL DEFAULT now()
);
