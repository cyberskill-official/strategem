-- Operator-only BYOK LLM settings (encrypted API key envelope).
-- Single-row active config; history via supersession (effective_to).

CREATE TABLE IF NOT EXISTS operator_llm_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_base_url TEXT NOT NULL,
  model_id TEXT NOT NULL,
  api_key_envelope JSONB,
  backend TEXT NOT NULL DEFAULT 'openai_compatible',
  updated_by UUID,
  effective_from TIMESTAMPTZ NOT NULL DEFAULT now(),
  effective_to TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS operator_llm_settings_one_active
  ON operator_llm_settings ((1))
  WHERE effective_to IS NULL;
