-- FR-PLAT-003: knowledge_patterns — table owned jointly with FR-RULE-001 (conditions DSL).
-- Seeded classical knowledge (FR-KB-002): world-readable, admin/curator write (see 0009).

CREATE TABLE knowledge_patterns (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  system      text NOT NULL,          -- qimen|liuren|taiyi|shared
  pattern_key text UNIQUE NOT NULL,   -- stable slug e.g. qimen_thanh_long_hoi_dau
  name        text NOT NULL,
  name_han    text,
  conditions  jsonb NOT NULL,         -- the FR-RULE-001 condition DSL
  polarity    text,                   -- cat|hung|trung
  score       real,
  citations   jsonb NOT NULL DEFAULT '[]',
  version     int NOT NULL DEFAULT 1,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);
