"use client";

import { displayPatternName, patternGloss } from "../../lib/domain/glossary";
import { useLocale } from "../i18n/locale-provider";

export type PatternItem = {
  id?: string;
  name: string;
  cung?: number | null;
  polarity?: string;
  score?: number | null;
  citations?: string[];
};

function PolarityBadge({ polarity }: { polarity?: string }) {
  const { t } = useLocale();
  const p = (polarity ?? "trung").toLowerCase();
  const key =
    p === "cat" ? "polarity.cat" : p === "hung" ? "polarity.hung" : "polarity.trung";
  const label = t(key);
  const icon = p === "cat" ? "▲" : p === "hung" ? "▼" : "◆";
  const cls =
    p === "cat" ? "cs-badge--cat" : p === "hung" ? "cs-badge--hung" : "cs-badge--trung";
  return (
    <span
      data-testid="polarity-badge"
      className={`cs-badge ${cls}`}
      aria-label={`${t("polarity.label")} ${label}`}
    >
      <span aria-hidden>{icon}</span>
      <span>{label}</span>
    </span>
  );
}

export function PatternList({ patterns }: { patterns: PatternItem[] }) {
  const { t, locale } = useLocale();
  if (!patterns.length) {
    return <p data-testid="patterns-empty">{t("results.patternsEmpty")}</p>;
  }
  return (
    <ul data-testid="pattern-list" style={{ listStyle: "none", padding: 0, margin: 0 }}>
      {patterns.map((p, i) => {
        const name = displayPatternName(p.name, locale);
        const gloss = patternGloss(p.name, locale);
        return (
          <li key={p.id ?? `${p.name}-${i}`} className="cs-pattern-row">
            <div>
              <strong>
                {name}
                {name !== p.name && /[\u4e00-\u9fff]/.test(p.name) ? (
                  <span className="cs-muted cs-pattern-classical">
                    {p.name}
                  </span>
                ) : null}
              </strong>
              <div className="cs-pattern-row__meta">
                {p.cung != null ? (
                  <span>
                    {t("chart.palace")} {p.cung}
                  </span>
                ) : null}
                {gloss ? <span>{p.cung != null ? " · " : ""}{gloss}</span> : null}
              </div>
            </div>
            <PolarityBadge polarity={p.polarity} />
          </li>
        );
      })}
    </ul>
  );
}
