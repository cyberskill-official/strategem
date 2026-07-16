-- TASK-AUTH-001: auth-owned users shape (coordinates with TASK-PLAT-003 umbrella).
-- PLAT-003 created base users; this migration adds AUTH columns when missing.
-- Apply after db/migrations/0002_users.sql (or as documentation of AUTH ownership).

-- email_verified (TASK-AUTH-003 completes the flow; default false at register)
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified boolean NOT NULL DEFAULT false;

-- preferences (language, default systems, school flags)
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences jsonb NOT NULL DEFAULT '{}'::jsonb;

-- birth_data as AES-256-GCM envelope (jsonb). PLAT-003 used birth_data_encrypted bytea;
-- AUTH stores the structured envelope here. Prefer birth_data for new writes.
ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_data jsonb;

-- social link columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS social_provider text;
ALTER TABLE users ADD COLUMN IF NOT EXISTS social_subject text;

COMMENT ON COLUMN users.birth_data IS
  'AES-256-GCM envelope {alg,iv,ct,tag,wrapped_dek}; never plaintext (TASK-AUTH-001 RISK-5).';
COMMENT ON COLUMN users.password_hash IS
  'argon2 hash; null for social-only accounts. Never log.';
