"use client";

import type { StructuredReport } from "../../lib/api/report";

const POLARITY: Record<
  string,
  { icon: string; text: string; color: string }
> = {
  cat: { icon: "▲", text: "Cát", color: "var(--color-success, #15803d)" },
  hung: { icon: "▼", text: "Hung", color: "var(--color-danger, #b91c1c)" },
  trung: { icon: "◆", text: "Trung", color: "var(--color-muted, #57534e)" },
};

/**
 * Deterministic region — chart summary + detected patterns (engine-only).
 * Polarity: color AND icon AND text (never color alone).
 */
export function ChartSummarySection({
  report,
}: {
  report: StructuredReport;
}) {
  const cs = report.chart_summary;
  return (
    <section
      data-testid="deterministic-region"
      aria-label="Deterministic chart summary and patterns"
      style={{
        border: "1px solid var(--color-border)",
        borderRadius: 8,
        padding: 16,
      }}
    >
      <h2 style={{ marginTop: 0 }}>Chart summary · engine</h2>
      <dl data-testid="chart-summary">
        <dt>Hệ</dt>
        <dd>{cs.he}</dd>
        <dt>Lịch pháp</dt>
        <dd>{cs.lich_phap_summary}</dd>
        <dt>Key positions</dt>
        <dd>
          <ul>
            {cs.key_positions.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </dd>
      </dl>
      <h3>Detected patterns</h3>
      <ul data-testid="detected-patterns">
        {report.detected_patterns.map((p) => {
          const pol = POLARITY[p.polarity] ?? POLARITY.trung;
          return (
            <li key={p.id} data-testid="pattern-row">
              <span>{p.name}</span>
              {p.cung != null ? <span> · cung {p.cung}</span> : null}
              <span
                className="polarity-badge"
                data-testid="polarity-badge"
                aria-label={`Polarity ${pol.text}`}
                style={{
                  marginLeft: 8,
                  color: pol.color,
                  fontWeight: 600,
                }}
              >
                <span aria-hidden>{pol.icon}</span> {pol.text}
              </span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
