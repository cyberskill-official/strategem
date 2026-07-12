"use client";

import { useMemo, useState } from "react";
import type { StructuredReport } from "../../lib/api/report";
import {
  composeReading,
  composeRecommendations,
  shouldReplaceReading,
} from "../../lib/domain/readings";
import { useLocale } from "../i18n/locale-provider";
import { AIDisclosureBadge } from "../domain/ai-disclosure-badge";
import { PersonaToggle } from "../results/persona-toggle";
import { CitationList } from "./citation-list";
import { RecommendationsList } from "./recommendations-list";

export function InterpretationSection({
  report,
}: {
  report: StructuredReport;
}) {
  const { t, locale } = useLocale();
  const [persona, setPersona] = useState<"beginner" | "expert">("beginner");
  const disc = report.ai_disclosure;
  const pending = disc.review_status === "pending";
  const patterns = report.detected_patterns;
  const he = report.chart_summary.he;

  const raw =
    persona === "beginner"
      ? report.interpretation.beginner
      : report.interpretation.expert;

  const text = useMemo(() => {
    if (shouldReplaceReading(raw, locale)) {
      return composeReading(
        {
          he,
          patterns: patterns.map((p) => ({
            name: p.name,
            polarity: p.polarity,
            cung: p.cung,
          })),
          persona,
        },
        locale,
      );
    }
    return raw;
  }, [raw, locale, he, patterns, persona]);

  const recs = useMemo(() => {
    if (
      report.interpretation.recommendations?.length &&
      !shouldReplaceReading(raw, locale)
    ) {
      return report.interpretation.recommendations;
    }
    return composeRecommendations(
      patterns.map((p) => ({ name: p.name })),
      locale,
    );
  }, [report.interpretation.recommendations, patterns, locale, raw]);

  return (
    <section
      data-testid="ai-region"
      className="cs-region cs-region--ai"
      aria-label={t("report.interpretation")}
    >
      <div
        style={{
          display: "flex",
          gap: 12,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <h2 style={{ margin: 0 }}>{t("report.interpretation")}</h2>
        <AIDisclosureBadge
          model={disc.model}
          limits={disc.limits || t("disclosure.limitsDefault")}
          citations={report.citations.map((c) => c.source)}
          reviewStatus={disc.review_status}
        />
        {pending ? (
          <span
            data-testid="not-yet-approved"
            role="status"
            className="cs-badge cs-badge--hung"
          >
            {t("report.notApproved")}
          </span>
        ) : null}
      </div>

      <div style={{ marginTop: 12 }}>
        <PersonaToggle value={persona} onChange={setPersona} />
      </div>

      <p data-testid="interpretation-text" className="cs-prose">
        {text}
      </p>

      <RecommendationsList items={recs} />
      <CitationList citations={report.citations} />

      <p data-testid="confidence-supporting" className="cs-muted">
        {t("report.confidence")}: {report.confidence.toFixed(2)}
      </p>
    </section>
  );
}
