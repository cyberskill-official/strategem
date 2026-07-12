-- FR-KB-001: relational graph tables (Postgres default store)
CREATE TABLE IF NOT EXISTS l2_node (
  id   text PRIMARY KEY,
  kind text NOT NULL,
  label text NOT NULL DEFAULT '',
  attrs jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS l2_edge (
  src   text NOT NULL REFERENCES l2_node(id),
  rel   text NOT NULL,
  dst   text NOT NULL REFERENCES l2_node(id),
  attrs jsonb NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (src, rel, dst)
);

CREATE INDEX IF NOT EXISTS l2_edge_src_idx ON l2_edge(src);
CREATE INDEX IF NOT EXISTS l2_edge_dst_idx ON l2_edge(dst);
CREATE INDEX IF NOT EXISTS l2_node_kind_idx ON l2_node(kind);
