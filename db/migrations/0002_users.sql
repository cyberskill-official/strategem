-- FR-PLAT-003: users table. Birth data is opaque ciphertext (FR-AUTH-001 encrypts).
-- Soft-delete via deleted_at supports erasure (FR-LEGAL-002).

CREATE TABLE users (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email                  citext UNIQUE NOT NULL,
  password_hash          text,                          -- null for social-only (FR-AUTH-001)
  display_name           text,
  tier                   text NOT NULL DEFAULT 'free',  -- free|premium|enterprise|admin (FR-AUTH-002)
  locale                 text NOT NULL DEFAULT 'vi',
  birth_data_encrypted   bytea,                         -- AES-256 ciphertext, opaque here (RISK-5)
  created_at             timestamptz NOT NULL DEFAULT now(),
  updated_at             timestamptz NOT NULL DEFAULT now(),
  deleted_at             timestamptz                     -- soft-delete for erasure (FR-LEGAL-002)
);

COMMENT ON COLUMN users.birth_data_encrypted IS
  'AES-256 ciphertext only; plaintext birth data MUST never be stored (FR-AUTH-001 / RISK-5).';
COMMENT ON COLUMN users.deleted_at IS
  'Soft-delete / erasure support for VN PDPD and GDPR (FR-LEGAL-002).';
