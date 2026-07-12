-- FR-KB-003 classical corpus tables (umbrella with PLAT-003 runner)

CREATE TABLE IF NOT EXISTS classical_sources (
  source_id text PRIMARY KEY,
  title text NOT NULL,
  system text NOT NULL,
  citation_prefix text NOT NULL,
  language text NOT NULL DEFAULT 'zh-vi'
);

CREATE TABLE IF NOT EXISTS classical_units (
  unit_id text PRIMARY KEY,
  source_id text NOT NULL REFERENCES classical_sources(source_id) ON DELETE CASCADE,
  citation_id text NOT NULL UNIQUE,
  unit_type text NOT NULL,
  ordinal int NOT NULL,
  system text NOT NULL,
  nguyen_van_han text,
  bach_thoai text,
  dich text,
  CONSTRAINT classical_units_at_least_one_layer CHECK (
    (nguyen_van_han IS NOT NULL AND length(trim(nguyen_van_han)) > 0)
    OR (bach_thoai IS NOT NULL AND length(trim(bach_thoai)) > 0)
    OR (dich IS NOT NULL AND length(trim(dich)) > 0)
  )
);

CREATE INDEX IF NOT EXISTS classical_units_source_ord ON classical_units (source_id, ordinal);
