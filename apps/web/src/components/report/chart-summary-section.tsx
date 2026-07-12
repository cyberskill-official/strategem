"use client";

import type { StructuredReport } from "../../lib/api/report";
import { useLocale } from "../i18n/locale-provider";

/**
 * Deterministic region — chart summary + detected patterns (engine-only).
 * Polarity: color AND icon AND text (never color alone).
 */
export function ChartSummarySection({
  report,
}: {
  report: StructuredReport;
}) {
  const { t } = useLocale();
  const cs = report.chart_summary;

  const polarity = (p: string) => {
    const key =
      p === "cat"
        ? "polarity.cat"
        : p === "hung"
          ? "polarity.hung"
          : "polarity.trung";
    const icon = p === "cat" ? "▲" : p === "hung" ? "▼" : "◆";
    const color =
      p === "cat"
        ? "var(--color-success, #15803d)"
        : p === "hung"
          ? "var(--color-danger, #b91c1c)"
          : "var(--color-muted, #57534e)";
    return { icon, text: t(key), color };
  };

  return (
    <section
      data-testid="deterministic-region"
      className="cs-region"
      aria-label={t("report.chartSummary")}
    >
      <h2 style={{ marginTop: 0 }}>{t("report.chartSummary")}</h2>
      <dl data-testid="chart-summary">
        <dt>{t("report.he")}</dt>
        <dd>{cs.he}</dd>
        <dt>{t("report.lichPhap")}</dt>
        <dd>{cs.lich_phap_summary}</dd>
        <dt>{t("report.keyPositions")}</dt>
        <dd>
          <ul>
            {cs.key_positions.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </dd>
      </dl>
      <h3>{t("report.patterns")}</h3>
      <ul data-testid="detected-patterns">
        {report.detected_patterns.map((p) => {
          const pol = polarity(p.polarity);
          return (
            <li key={p.id} data-testid="pattern-row">
              <span>{p.name}</span>
              {p.cung != null ? (
                <span>
                  {" "}
                  · {t("chart.palace")} {p.cung}
                </span>
              ) : null}
              <span
                className="polarity-badge"
                data-testid="polarity-badge"
                aria-label={`${t("polarity.label")} ${pol.text}`}
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
