-- FR-PLAT-003: audit_logs — sensitive-access trail (strategy 4.4, RISK-5). Append-mostly.

CREATE TABLE audit_logs (
  id            bigserial PRIMARY KEY,
  user_id       uuid REFERENCES users(id) ON DELETE SET NULL,
  action        text NOT NULL,        -- e.g. chart.cast, report.read, user.erase
  resource_type text,
  resource_id   text,
  request_id    text,
  ip            inet,
  metadata      jsonb NOT NULL DEFAULT '{}',
  created_at    timestamptz NOT NULL DEFAULT now()
);
