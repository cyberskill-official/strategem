-- TT-024: fold AUTH user columns into the shared migration chain.
-- Mirrors packages/tamthuc_auth/migrations/0001_users.sql for db_schema.migrate / migrate.sh.

ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified boolean NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences jsonb NOT NULL DEFAULT '{}'::jsonb;
-- Structured AES-256-GCM envelope (jsonb). Prefer this over birth_data_encrypted bytea.
ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_data jsonb;
ALTER TABLE users ADD COLUMN IF NOT EXISTS social_provider text;
ALTER TABLE users ADD COLUMN IF NOT EXISTS social_subject text;

COMMENT ON COLUMN users.birth_data IS
  'AES-256-GCM envelope {alg,iv,ct,tag,wrapped_dek}; never plaintext (TASK-AUTH-001 / TT-024).';
COMMENT ON COLUMN users.password_hash IS
  'argon2 hash; null for social-only accounts. Never log.';
