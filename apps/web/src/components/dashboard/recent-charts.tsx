"use client";

import Link from "next/link";

export type ChartRef = {
  query_id: string;
  he: string;
  question_type: string;
  cast_at: string;
};

export function RecentCharts({
  charts,
  title,
  emptyHint = "No charts yet — cast your first chart.",
}: {
  charts: ChartRef[];
  title: string;
  emptyHint?: string;
}) {
  return (
    <section data-testid="recent-charts">
      <h2>{title}</h2>
      {!charts.length ? (
        <p data-testid="charts-empty">{emptyHint}</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, display: "flex", gap: 12, flexWrap: "wrap" }}>
          {charts.map((c) => (
            <li key={c.query_id}>
              <Link
                href={`/results/${c.query_id}`}
                style={{
                  display: "block",
                  border: "1px solid var(--color-border)",
                  borderRadius: 8,
                  padding: 12,
                  minWidth: 160,
                  textDecoration: "none",
                  color: "inherit",
                }}
              >
                <div style={{ fontWeight: 600 }}>{c.he}</div>
                <div style={{ fontSize: 12 }}>{c.question_type}</div>
                <div style={{ fontSize: 11, opacity: 0.7 }}>{c.cast_at}</div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
