"use client";

import { useMemo, useState } from "react";
import { useLocale } from "../i18n/locale-provider";
import { cellsFromBan } from "../chart/qimen-nine-palace";
import { LiurenChart } from "../chart/liuren-chart";
import { PalaceDetailSidebar } from "../chart/palace-detail-sidebar";
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
import { composeStorySummary, rankPatterns } from "../../lib/domain/readings";

export type QueryResponseView = {
  query_id: string;
  charts?: Record<
    string,
    { ban?: Record<string, unknown>; he?: string; cach_cuc?: PatternItem[] }
  >;
  patterns?: PatternItem[];
  interpretation?: InterpretationData | null;
  ai_disclosure?: DisclosureData | null;
  /** soft meta for header strip */
  place?: string;
  cast_at?: string;
  engine_mode?: "cast_cli" | "local_fallback" | "demo" | "unknown";
};

/**
 * Results right panel — TASK-WEB-003 + trust hierarchy.
 * Story first; technical board behind progressive disclosure.
 * Envelope is read-only; this component never mutates ban/cach_cuc.
 */
export function ResultsPanel({ response }: { response: QueryResponseView }) {
  const { t, locale } = useLocale();
  const [selected, setSelected] = useState<number | null>(null);
  const [showBoard, setShowBoard] = useState(false);
  const [showAi, setShowAi] = useState(false);

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

  const ranked = useMemo(() => rankPatterns(patterns), [patterns]);
  const best = ranked[0];

  const isDemo =
    response.query_id.startsWith("demo-") || response.engine_mode === "demo";

  const systemLabel = (() => {
    if (!he) return null;
    const key = `system.${he}`;
    const label = t(key);
    return label.startsWith("[missing:") ? he : label;
  })();

  const engineBadge = (() => {
    if (isDemo) return t("results.engine.demo");
    if (response.engine_mode === "local_fallback") return t("results.engine.local");
    if (response.engine_mode === "cast_cli") return t("results.engine.live");
    return null;
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

  const story = composeStorySummary(
    { he, patterns, persona: "beginner" },
    locale,
  );

  return (
    <div data-testid="results-panel" className="cs-results-stack">
      {isDemo ? (
        <div className="cs-banner cs-banner--ochre">{t("results.demoBanner")}</div>
      ) : null}
      {engineBadge && !isDemo ? (
        <div
          className={`cs-banner ${
            response.engine_mode === "local_fallback"
              ? "cs-banner--ochre"
              : "cs-banner--info"
          }`}
          data-testid="engine-mode-badge"
        >
          {engineBadge}
        </div>
      ) : null}

      <section
        className="cs-story-summary"
        data-testid="results-story-summary"
        aria-label={t("results.storyTitle")}
      >
        <h2>{t("results.storyTitle")}</h2>
        <p className="cs-muted">{t("results.storyLead")}</p>
        <div className="cs-story-narrative" data-testid="results-story-narrative">
          {story.lines.map((line, i) => (
            <p key={i} className={i === 0 ? "cs-story-narrative__lead" : "cs-muted"}>
              {line}
            </p>
          ))}
        </div>
        {systemLabel || best?.name ? (
          <div className="cs-story-chips">
            {systemLabel ? (
              <span className="cs-badge cs-badge--trung">{systemLabel}</span>
            ) : null}
            {best?.name ? (
              <span
                className={`cs-badge ${
                  (best.polarity ?? "").toLowerCase() === "hung"
                    ? "cs-badge--hung"
                    : (best.polarity ?? "").toLowerCase() === "cat"
                      ? "cs-badge--cat"
                      : "cs-badge--trung"
                }`}
              >
                {displayPatternName(best.name, locale)}
              </span>
            ) : null}
          </div>
        ) : null}
        <p className="cs-disclaimer" data-testid="results-disclaimer-mid">
          {t("results.disclaimer.mid")}
        </p>
      </section>

      <div className="cs-results-actions">
        <button
          type="button"
          className="cs-link-btn cs-link-btn--secondary"
          data-testid="toggle-board"
          aria-expanded={showBoard}
          onClick={() => setShowBoard((v) => !v)}
        >
          {showBoard ? t("results.chartHide") : t("results.chartToggle")}
        </button>
      </div>

      {showBoard ? (
        <section
          data-testid="deterministic-region"
          className="cs-region"
          aria-label={t("results.chartRegion")}
        >
          <div className="cs-section-title">
            <h2>{t("results.chartRegion")}</h2>
            {systemLabel ? (
              <span className="cs-badge cs-badge--trung">{systemLabel}</span>
            ) : null}
          </div>
          {/* COV-017: board + palace detail sidebar */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "minmax(0, 1fr) minmax(200px, 280px)",
              gap: "1rem",
              alignItems: "start",
            }}
            data-testid="chart-with-sidebar"
          >
            <div>{renderBoard()}</div>
            <PalaceDetailSidebar
              selected={selected}
              cell={
                he === "ky_mon" || he === "qimen" || !he
                  ? cellsFromBan(chart?.ban as Parameters<typeof cellsFromBan>[0]).find(
                      (c) => c.palace === selected,
                    )
                  : selected != null
                    ? {
                        palace: selected,
                        stem: undefined,
                        star: undefined,
                        door: undefined,
                        god: undefined,
                      }
                    : null
              }
              patterns={patterns}
              system={he || "qimen"}
              onClose={() => setSelected(null)}
            />
          </div>
          <h3 className="cs-subhead">{t("results.patterns")}</h3>
          <PatternList
            patterns={
              (ranked.length ? ranked : patterns).filter(
                (p): p is PatternItem => typeof p.name === "string" && p.name.length > 0,
              )
            }
          />
        </section>
      ) : null}

      <button
        type="button"
        className="cs-advanced-toggle"
        data-testid="toggle-ai"
        aria-expanded={showAi}
        onClick={() => setShowAi((v) => !v)}
      >
        {showAi ? "▾ " : "▸ "}
        {t("results.aiMore")}
      </button>

      {showAi ? (
        <>
          <hr data-testid="region-boundary" className="cs-region-boundary" aria-hidden />
          <section
            data-testid="ai-region"
            className="cs-region cs-region--ai"
            aria-label={t("results.aiRegion")}
          >
            <h2>{t("results.aiRegion")}</h2>
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
        </>
      ) : null}

      <details className="cs-tech-details" data-testid="tech-details">
        <summary>{t("results.techDetails")}</summary>
        <p className="cs-muted">
          {t("results.techId")}:{" "}
          <code className="cs-mono">{response.query_id}</code>
        </p>
        {he ? (
          <p className="cs-muted">
            he=<code className="cs-mono">{he}</code>
          </p>
        ) : null}
        {/* COV-003: stamped school + calendar flags from envelope */}
        {chart && typeof chart === "object" ? (
          <div data-testid="stamped-flags" className="cs-muted" style={{ marginTop: 8 }}>
            <p style={{ fontWeight: 600 }}>{t("results.stampedFlags")}</p>
            <pre
              className="cs-mono"
              style={{ fontSize: 11, whiteSpace: "pre-wrap", margin: 0 }}
            >
              {JSON.stringify(
                {
                  co_truong_phai:
                    (chart as { co_truong_phai?: unknown }).co_truong_phai ?? null,
                  co_lich_phap:
                    (
                      (chart as { lich_phap?: { co_lich_phap?: unknown } }).lich_phap ||
                      {}
                    ).co_lich_phap ?? null,
                },
                null,
                2,
              )}
            </pre>
          </div>
        ) : null}
      </details>

      <NextStepCard
        systemLabel={systemLabel ?? undefined}
        patternHint={
          best?.name ? displayPatternName(best.name, locale) : undefined
        }
      />
    </div>
  );
}
