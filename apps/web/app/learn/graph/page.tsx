"use client";

/** COV-022 — lightweight knowledge-graph explorer (stored edges only). */

import { useCallback, useEffect, useState } from "react";
import { useLocale } from "../../../src/components/i18n/locale-provider";
import { apiBase } from "../../../src/lib/api/client";

type Node = { id: string; label?: string; kind?: string };
type Neighbor = { node_id: string; rel: string; direction: string; label?: string };

export default function GraphExplorerPage() {
  const { t } = useLocale();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [selected, setSelected] = useState("ngu_hanh_moc");
  const [neighbors, setNeighbors] = useState<Neighbor[]>([]);
  const [error, setError] = useState<string | null>(null);

  const loadNodes = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase()}/api/v1/knowledge/graph/nodes`);
      const body = await res.json();
      setNodes(body.nodes || []);
      if ((body.nodes || [])[0]?.id) setSelected((s) => s || body.nodes[0].id);
    } catch {
      setError(t("graph.error"));
    }
  }, [t]);

  const loadNeighbors = useCallback(async () => {
    if (!selected) return;
    try {
      const res = await fetch(
        `${apiBase()}/api/v1/knowledge/graph/neighbors?node_id=${encodeURIComponent(selected)}`,
      );
      const body = await res.json();
      setNeighbors(body.neighbors || []);
    } catch {
      setError(t("graph.error"));
    }
  }, [selected, t]);

  useEffect(() => {
    let cancelled = false;
    const t = window.setTimeout(() => {
      void (async () => {
        if (cancelled) return;
        await loadNodes();
      })();
    }, 0);
    return () => {
      cancelled = true;
      window.clearTimeout(t);
    };
  }, [loadNodes]);

  useEffect(() => {
    let cancelled = false;
    const t = window.setTimeout(() => {
      void (async () => {
        if (cancelled) return;
        await loadNeighbors();
      })();
    }, 0);
    return () => {
      cancelled = true;
      window.clearTimeout(t);
    };
  }, [loadNeighbors]);

  return (
    <div className="cs-page cs-reveal" data-testid="graph-explorer-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("graph.kicker")}</p>
        <h1>{t("graph.title")}</h1>
        <p className="cs-lead-short">{t("graph.subtitle")}</p>
      </header>

      <div className="cs-card">
        <label>
          <span className="cs-muted">{t("graph.node")}</span>
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            data-testid="graph-node-select"
          >
            {(nodes.length
              ? nodes
              : [
                  { id: "ngu_hanh_moc" },
                  { id: "ngu_hanh_hoa" },
                  { id: "ngu_hanh_tho" },
                  { id: "ngu_hanh_kim" },
                  { id: "ngu_hanh_thuy" },
                ]
            ).map((n) => (
              <option key={n.id} value={n.id}>
                {n.label || n.id}
              </option>
            ))}
          </select>
        </label>
        <p className="cs-muted" style={{ fontSize: "0.85rem", marginTop: 8 }}>
          {t("graph.note")}
        </p>
      </div>

      {error ? (
        <p role="alert" className="cs-card">
          {error}
        </p>
      ) : null}

      <section className="cs-card" style={{ marginTop: "1rem" }} data-testid="graph-neighbors">
        <h2>{t("graph.neighbors")}</h2>
        <ul>
          {neighbors.map((n, i) => (
            <li key={`${n.node_id}-${i}`}>
              <strong>{n.rel}</strong> {n.direction} → {n.label || n.node_id}
            </li>
          ))}
        </ul>
        {!neighbors.length ? <p className="cs-muted">{t("graph.empty")}</p> : null}
      </section>
    </div>
  );
}
