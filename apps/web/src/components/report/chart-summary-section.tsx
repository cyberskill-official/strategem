"use client";

import type { StructuredReport } from "../../lib/api/report";
import { displayPatternName, patternGloss } from "../../lib/domain/glossary";
import { useLocale } from "../i18n/locale-provider";

export function ChartSummarySection({
  report,
}: {
  report: StructuredReport;
}) {
  const { t, locale } = useLocale();
  const cs = report.chart_summary;

  const polarity = (p: string) => {
    const key =
      p === "cat"
        ? "polarity.cat"
        : p === "hung"
          ? "polarity.hung"
          : "polarity.trung";
    const icon = p === "cat" ? "▲" : p === "hung" ? "▼" : "◆";
    const cls =
      p === "cat" ? "cs-badge--cat" : p === "hung" ? "cs-badge--hung" : "cs-badge--trung";
    return { icon, text: t(key), cls };
  };

  return (
    <section
      data-testid="deterministic-region"
      className="cs-region"
      aria-label={t("report.chartSummary")}
    >
      <h2 style={{ marginTop: 0 }}>{t("report.chartSummary")}</h2>
      <dl data-testid="chart-summary" className="cs-grid-3" style={{ gap: 12 }}>
        <div className="cs-stat">
          <dt className="cs-stat__label">{t("report.he")}</dt>
          <dd className="cs-stat__value" style={{ fontSize: "1.05rem" }}>
            {t(`system.${cs.he}`).startsWith("[missing:")
              ? cs.he
              : t(`system.${cs.he}`)}
          </dd>
        </div>
        <div className="cs-stat" style={{ gridColumn: "span 2" }}>
          <dt className="cs-stat__label">{t("report.lichPhap")}</dt>
          <dd style={{ margin: 0, fontWeight: 600 }}>{cs.lich_phap_summary}</dd>
        </div>
      </dl>
      <h3 style={{ marginTop: 20 }}>{t("report.keyPositions")}</h3>
      <ul>
        {cs.key_positions.map((p) => (
          <li key={p}>{p}</li>
        ))}
      </ul>
      <h3>{t("report.patterns")}</h3>
      <ul data-testid="detected-patterns" style={{ listStyle: "none", padding: 0 }}>
        {report.detected_patterns.map((p) => {
          const pol = polarity(p.polarity);
          const name = displayPatternName(p.name, locale);
          const gloss = patternGloss(p.name, locale);
          return (
            <li key={p.id} data-testid="pattern-row" className="cs-pattern-row">
              <div>
                <strong>{name}</strong>
                {p.cung != null ? (
                  <span className="cs-muted">
                    {" "}
                    · {t("chart.palace")} {p.cung}
                  </span>
                ) : null}
                {gloss ? (
                  <div className="cs-pattern-row__meta">{gloss}</div>
                ) : null}
              </div>
              <span
                className={`cs-badge ${pol.cls} polarity-badge`}
                data-testid="polarity-badge"
                aria-label={`${t("polarity.label")} ${pol.text}`}
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
