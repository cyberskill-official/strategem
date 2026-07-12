"use client";

import { useEffect, useState } from "react";
import { HistoryList } from "../../../src/components/manage/history-list";
import { getHistory, type ChartRef } from "../../../src/lib/api/history";

/** Management flow — history — FR-WEB-007 (live API, no demo fixtures). */
export default function ManageHistoryPage() {
  const [items, setItems] = useState<ChartRef[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const rows = await getHistory();
        if (!cancelled) setItems(rows);
      } catch (e) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : "Failed to load history");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: 16 }}>
      <h1>History</h1>
      {loading ? <p data-testid="history-loading">Loading…</p> : null}
      {error ? (
        <p data-testid="history-error" style={{ color: "var(--color-danger)" }}>
          {error} — cast a chart first, and ensure the API is running.
        </p>
      ) : null}
      {!loading && !error && items.length === 0 ? (
        <p data-testid="history-empty">No saved casts yet.</p>
      ) : null}
      {!loading && items.length > 0 ? <HistoryList items={items} /> : null}
    </div>
  );
}
