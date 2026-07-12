-- FR-PLAT-003: GIN on JSONB containment paths + btree helpers for hot paths.

CREATE INDEX charts_envelope_gin        ON charts             USING gin (envelope       jsonb_path_ops);
CREATE INDEX patterns_conditions_gin    ON knowledge_patterns USING gin (conditions     jsonb_path_ops);
CREATE INDEX reports_interpretation_gin ON reports            USING gin (interpretation jsonb_path_ops);

CREATE INDEX charts_cache_key_idx ON charts (cache_key);
CREATE INDEX queries_user_id_idx  ON queries (user_id);
CREATE INDEX audit_user_time_idx  ON audit_logs (user_id, created_at);
