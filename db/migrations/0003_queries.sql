-- FR-PLAT-003: queries — user-scoped cast requests (question + datetime + flags).

CREATE TABLE queries (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  datetime       text NOT NULL,       -- ISO local time of the question/event
  tz             text NOT NULL,       -- e.g. "+07:00"
  kinh_do        double precision,    -- longitude
  place          text,
  question_type  text NOT NULL,       -- loai_cau_hoi
  systems        text[] NOT NULL,     -- ["qimen"] | ["qimen","liuren"] | ["all"]
  persona_level  text NOT NULL DEFAULT 'beginner',
  co_truong_phai jsonb,               -- school-flag overrides (else engine defaults)
  created_at     timestamptz NOT NULL DEFAULT now()
);
