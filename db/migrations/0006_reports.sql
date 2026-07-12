-- FR-PLAT-003: reports — structured interpretation (FR-RAG-003) + mandatory AI disclosure.

CREATE TABLE reports (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  query_id       uuid NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
  user_id        uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  interpretation jsonb NOT NULL,      -- the FR-RAG-003 Interpretation object
  ai_disclosure  jsonb NOT NULL,      -- AIDisclosure block (mandatory)
  review_status  text NOT NULL DEFAULT 'not_required',  -- pending|not_required|approved|rejected
  pdf_url        text,
  created_at     timestamptz NOT NULL DEFAULT now()
);
