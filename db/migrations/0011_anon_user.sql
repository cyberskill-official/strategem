-- W2: well-known anonymous principal for local/enterprise casts that write
-- RLS domain tables (queries/charts/reports/audit_logs) without a JWT subject.
-- Auth-registered users are upserted by the API on first persist.

INSERT INTO users (id, email, display_name, tier, locale)
VALUES (
  '00000000-0000-4000-8000-0000000000a1',
  'anon@strategem.local',
  'Anonymous cast',
  'free',
  'vi'
)
ON CONFLICT (id) DO NOTHING;
