-- Durable PayOS webhook idempotency (single-rail payments).
-- Prevents duplicate premium fulfillment on webhook replay.

CREATE TABLE IF NOT EXISTS payment_fulfillments (
  event_key TEXT PRIMARY KEY,
  user_id UUID NOT NULL,
  provider TEXT NOT NULL DEFAULT 'payos',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS payment_fulfillments_user_id_idx
  ON payment_fulfillments (user_id);
