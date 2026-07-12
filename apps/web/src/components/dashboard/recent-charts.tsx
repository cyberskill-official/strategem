"use client";

import Link from "next/link";
import { useLocale } from "../i18n/locale-provider";

export type ChartRef = {
  query_id: string;
  he: string;
  question_type: string;
  cast_at: string;
};

export function RecentCharts({
  charts,
  title,
  emptyHint,
}: {
  charts: ChartRef[];
  title: string;
  emptyHint?: string;
}) {
  const { t } = useLocale();
  const empty = emptyHint ?? t("dashboard.recentEmpty");

  const systemLabel = (he: string) => {
    const key = `system.${he}`;
    const label = t(key);
    return label.startsWith("[missing:") ? he : label;
  };
  const questionLabel = (q: string) => {
    const key = `cast.q.${q}`;
    const label = t(key);
    return label.startsWith("[missing:") ? q : label;
  };

  return (
    <section data-testid="recent-charts">
      <h2>{title}</h2>
      {!charts.length ? (
        <p data-testid="charts-empty" className="cs-muted">
          {empty}
        </p>
      ) : (
        <ul
          style={{
            listStyle: "none",
            padding: 0,
            margin: 0,
            display: "flex",
            gap: 12,
            flexWrap: "wrap",
          }}
        >
          {charts.map((c) => (
            <li key={c.query_id}>
              <Link
                href={`/results/${c.query_id}`}
                className="cs-card"
                style={{
                  display: "block",
                  minWidth: 160,
                  padding: 12,
                  textDecoration: "none",
                  color: "inherit",
                }}
              >
                <div style={{ fontWeight: 600 }}>{systemLabel(c.he)}</div>
                <div className="cs-muted">{questionLabel(c.question_type)}</div>
                <div className="cs-muted" style={{ fontSize: 11 }}>
                  {c.cast_at}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
