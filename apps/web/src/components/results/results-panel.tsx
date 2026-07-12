"use client";

import { useMemo, useState } from "react";
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
  const [selected, setSelected] = useState<number | null>(null);

  // Read-only snapshot — do not mutate
  const chart = useMemo(() => {
    const charts = response.charts ?? {};
    const first = Object.values(charts)[0];
    return first;
  }, [response.charts]);

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

  return (
    <div data-testid="results-panel" style={{ display: "grid", gap: 24 }}>
      <section
        data-testid="deterministic-region"
        aria-label="Deterministic chart and patterns"
        style={{
          border: "1px solid var(--color-border)",
          borderRadius: 8,
          padding: 16,
        }}
      >
        <h2 style={{ marginTop: 0 }}>Chart · engine</h2>
        <QimenNinePalace
          ban={ban}
          selectedPalace={selected}
          onSelectPalace={setSelected}
        />
        <h3>Detected patterns</h3>
        <PatternList patterns={patterns} />
      </section>

      <hr
        data-testid="region-boundary"
        style={{ border: "none", borderTop: "2px dashed var(--color-border)" }}
        aria-hidden
      />

      <section
        data-testid="ai-region"
        aria-label="AI interpretation"
        style={{
          border: "1px solid var(--color-border)",
          borderRadius: 8,
          padding: 16,
          background: "var(--color-surface)",
        }}
      >
        <h2 style={{ marginTop: 0 }}>Interpretation · AI</h2>
        {response.interpretation ? (
          <InterpretationView
            interpretation={response.interpretation}
            disclosure={response.ai_disclosure}
          />
        ) : (
          <p data-testid="no-interpretation">No interpretation available.</p>
        )}
      </section>
    </div>
  );
}
