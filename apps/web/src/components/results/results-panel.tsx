"use client";

import { useMemo, useState } from "react";
import { useLocale } from "../i18n/locale-provider";
import { LiurenChart } from "../chart/liuren-chart";
import { QimenNinePalace } from "../chart/qimen-nine-palace";
import { TaiyiChart } from "../chart/taiyi-chart";
import {
  InterpretationView,
  type DisclosureData,
  type InterpretationData,
} from "./interpretation-view";
import { NextStepCard } from "./next-step-card";
import { PatternList, type PatternItem } from "./pattern-list";
import { displayPatternName } from "../../lib/domain/glossary";
import { composeStorySummary } from "../../lib/domain/readings";

export type QueryResponseView = {
  query_id: string;
  charts?: Record<
    string,
    { ban?: Record<string, unknown>; he?: string; cach_cuc?: PatternItem[] }
  >;
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
  const { t, locale } = useLocale();
  const [selected, setSelected] = useState<number | null>(null);

  const chart = useMemo(() => {
    const charts = response.charts ?? {};
    return Object.values(charts)[0];
  }, [response.charts]);

  const he = (chart?.he ?? "").toLowerCase();

  const patterns: PatternItem[] = useMemo(() => {
    if (response.patterns?.length) return response.patterns;
    const cc = chart?.cach_cuc;
    return Array.isArray(cc) ? (cc as PatternItem[]) : [];
  }, [response.patterns, chart]);

  const isDemo = response.query_id.startsWith("demo-");

  const systemLabel = (() => {
    if (!he) return null;
    const key = `system.${he}`;
    const label = t(key);
    return label.startsWith("[missing:") ? he : label;
  })();

  function renderBoard() {
    const ban = chart?.ban ?? {};
    if (he === "luc_nham" || he === "liuren") {
      return (
        <LiurenChart
          laso={{
            he: "luc_nham",
            ban: ban as import("../../lib/chart/read-luc-nham-ban").LucNhamBan,
            cach_cuc: patterns.map((p) => ({
              name: p.name,
              polarity: p.polarity,
              cung: p.cung ?? undefined,
            })),
          }}
        />
      );
    }
    if (he === "thai_at" || he === "taiyi") {
      return (
        <TaiyiChart
          laso={{
            he: "thai_at",
            ban: ban as import("../../lib/chart/read-thai-at-ban").ThaiAtBanView,
            cach_cuc: patterns.map((p) => ({
              name: p.name,
              polarity: p.polarity,
            })),
          }}
        />
      );
    }
    // ky_mon / qimen default
    return (
      <QimenNinePalace
        ban={
          ban as {
            dia_ban?: string[];
            thien_ban?: string[];
            cuu_tinh?: string[];
            bat_mon?: (string | null)[];
            bat_than?: (string | null)[];
            dinh_cuc?: { so_cuc?: number; duong_don?: boolean };
          }
        }
        selectedPalace={selected}
        onSelectPalace={setSelected}
      />
    );
  }

  return (
    <div
      data-testid="results-panel"
      className="cs-stagger"
      style={{ display: "grid", gap: 24 }}
    >
      {isDemo ? (
        <div className="cs-banner cs-banner--ochre">{t("results.demoBanner")}</div>
      ) : null}

      <section
        className="cs-story-summary"
        data-testid="results-story-summary"
        aria-label={t("results.storyTitle")}
      >
        <h2>{t("results.storyTitle")}</h2>
        <p className="cs-muted">{t("results.storyLead")}</p>
        {(() => {
          const story = composeStorySummary(
            { he, patterns, persona: "beginner" },
            locale,
          );
          return (
            <div className="cs-story-narrative" data-testid="results-story-narrative">
              {story.lines.map((line, i) => (
                <p key={i} className={i === 0 ? "cs-story-narrative__lead" : "cs-muted"}>
                  {line}
                </p>
              ))}
            </div>
          );
        })()}
        {systemLabel || patterns[0] ? (
          <div className="cs-story-chips">
            {systemLabel ? (
              <span className="cs-badge cs-badge--trung">{systemLabel}</span>
            ) : null}
            {patterns[0]?.name ? (
              <span
                className={`cs-badge ${
                  (patterns[0].polarity ?? "").toLowerCase() === "hung"
                    ? "cs-badge--hung"
                    : (patterns[0].polarity ?? "").toLowerCase() === "cat"
                      ? "cs-badge--cat"
                      : "cs-badge--trung"
                }`}
              >
                {displayPatternName(patterns[0].name, locale)}
              </span>
            ) : null}
          </div>
        ) : null}
      </section>

      <section
        data-testid="deterministic-region"
        className="cs-region"
        aria-label={t("results.chartRegion")}
      >
        <div className="cs-section-title" style={{ marginBottom: 12 }}>
          <h2 style={{ marginTop: 0 }}>{t("results.chartRegion")}</h2>
          {systemLabel ? (
            <span className="cs-badge cs-badge--trung">{systemLabel}</span>
          ) : null}
        </div>
        {renderBoard()}
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
            he={he || undefined}
          />
        ) : (
          <p data-testid="no-interpretation">{t("results.noInterpretation")}</p>
        )}
      </section>

      <NextStepCard
        systemLabel={systemLabel ?? undefined}
        patternHint={
          patterns[0]?.name
            ? displayPatternName(patterns[0].name, locale)
            : undefined
        }
      />
    </div>
  );
}
