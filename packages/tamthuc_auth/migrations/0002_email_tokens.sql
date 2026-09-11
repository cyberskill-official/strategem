-- TASK-AUTH-003: hashed, single-use, expiring email tokens (verify + reset).
-- Applied via db/migrations/0018_email_tokens.sql in the shared PLAT chain.

CREATE TABLE IF NOT EXISTS email_tokens (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id),
  purpose     text NOT NULL CHECK (purpose IN ('email_verify', 'password_reset')),
  token_hash  text NOT NULL,
  expires_at  timestamptz NOT NULL,
  consumed_at timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS email_tokens_token_hash_uidx
  ON email_tokens (token_hash);

CREATE INDEX IF NOT EXISTS email_tokens_user_purpose_idx
  ON email_tokens (user_id, purpose)
  WHERE consumed_at IS NULL;
