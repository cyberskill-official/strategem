"use client";

import { useMemo, useState } from "react";
import { useLocale } from "../i18n/locale-provider";
import { QimenNinePalace } from "../chart/qimen-nine-palace";
import { InterpretationView, type DisclosureData, type InterpretationData } from "./interpretation-view";
import { PatternList, type PatternItem } from "./pattern-list";

export type QueryResponseView = {
  query_id: string;
  charts?: Record<string, { ban?: Record<string, unknown>; he?: string; cach_cuc?: PatternItem[] }>;
  patterns?: PatternItem[];
  interpretation?: InterpretationData | null;
  ai_disclosure?: DisclosureData | null;
};

/**
 * Results right panel — FR-WEB-003.
 * Deterministic region (chart + patterns) is visually separated from AI region.
 * Envelope is read-only; this component never mutates ban/cach_cuc.
 */
export function ResultsPanel({ response }: { response: QueryResponseView }) {
  const { t } = useLocale();
  const [selected, setSelected] = useState<number | null>(null);

  const chart = useMemo(() => {
    const charts = response.charts ?? {};
    return Object.values(charts)[0];
  }, [response.charts]);

  const he = chart?.he;

  const patterns: PatternItem[] = useMemo(() => {
    if (response.patterns?.length) return response.patterns;
    const cc = chart?.cach_cuc;
    return Array.isArray(cc) ? cc : [];
  }, [response.patterns, chart]);

  const ban = (chart?.ban ?? {}) as {
    dia_ban?: string[];
    thien_ban?: string[];
    cuu_tinh?: string[];
    bat_mon?: (string | null)[];
    bat_than?: (string | null)[];
    dinh_cuc?: { so_cuc?: number; duong_don?: boolean };
  };

  const isDemo = response.query_id.startsWith("demo-");

  return (
    <div data-testid="results-panel" className="cs-stagger" style={{ display: "grid", gap: 24 }}>
      {isDemo ? (
        <div className="cs-banner cs-banner--ochre">{t("results.demoBanner")}</div>
      ) : null}

      <section
        data-testid="deterministic-region"
        className="cs-region"
        aria-label={t("results.chartRegion")}
      >
        <div className="cs-section-title" style={{ marginBottom: 12 }}>
          <h2 style={{ marginTop: 0 }}>{t("results.chartRegion")}</h2>
          {he ? (
            <span className="cs-badge cs-badge--trung">
              {t(`system.${he}`).startsWith("[missing:") ? he : t(`system.${he}`)}
            </span>
          ) : null}
        </div>
        <QimenNinePalace
          ban={ban}
          selectedPalace={selected}
          onSelectPalace={setSelected}
        />
        <h3 style={{ marginTop: 20 }}>{t("results.patterns")}</h3>
        <PatternList patterns={patterns} />
      </section>

      <hr data-testid="region-boundary" className="cs-region-boundary" aria-hidden />

      <section
        data-testid="ai-region"
        className="cs-region cs-region--ai"
        aria-label={t("results.aiRegion")}
      >
        <h2 style={{ marginTop: 0 }}>{t("results.aiRegion")}</h2>
        {response.interpretation || patterns.length ? (
          <InterpretationView
            interpretation={
              response.interpretation ?? {
                beginner: "",
                expert: "",
                recommendations: [],
                citations: [],
              }
            }
            disclosure={response.ai_disclosure}
            patterns={patterns}
            he={he}
          />
        ) : (
          <p data-testid="no-interpretation">{t("results.noInterpretation")}</p>
        )}
      </section>
    </div>
  );
}
