-- AUTH-001 follow-up / TASK-AUTH-003: durable hashed email verification + password-reset tokens.
-- Mirrors packages/tamthuc_auth/migrations/0002_email_tokens.sql.

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

COMMENT ON TABLE email_tokens IS
  'Hashed single-use email_verify / password_reset tokens; raw token never stored.';

-- Service-role access (not user-scoped RLS): auth backend issues/consumes by hash.
GRANT SELECT, INSERT, UPDATE ON email_tokens TO app_user, app_admin;
