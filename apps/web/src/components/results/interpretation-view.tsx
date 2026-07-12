"use client";

import { useMemo, useState } from "react";
import {
  composeReading,
  composeRecommendations,
  shouldReplaceReading,
} from "../../lib/domain/readings";
import { useLocale } from "../i18n/locale-provider";
import { AIDisclosureBadge } from "../domain/ai-disclosure-badge";
import { HumanReviewGate } from "../domain/human-review-gate";
import { CitationCard } from "./citation-card";
import { PersonaToggle, type Persona } from "./persona-toggle";

export type InterpretationData = {
  beginner?: string;
  expert?: string;
  recommendations?: Array<string | { text?: string; citations?: string[] }>;
  citations?: Array<{
    citation_id?: string;
    source?: string;
    locator?: string;
    layers?: Record<string, string>;
    han?: string;
    bach_thoai?: string;
    dich?: string;
  }>;
  requires_human_review?: boolean;
  confidence?: number;
};

export type DisclosureData = {
  model?: string;
  limits?: string;
  review_status?: "pending" | "not_required" | "approved" | "rejected";
  retrieved_citation_ids?: string[];
  degraded?: boolean;
};

export function InterpretationView({
  interpretation,
  disclosure,
  patterns = [],
  he,
}: {
  interpretation: InterpretationData;
  disclosure?: DisclosureData | null;
  patterns?: Array<{ name?: string; polarity?: string; cung?: number | null }>;
  he?: string;
}) {
  const { t, locale } = useLocale();
  const [persona, setPersona] = useState<Persona>("beginner");

  const raw =
    persona === "expert"
      ? interpretation.expert ?? interpretation.beginner ?? ""
      : interpretation.beginner ?? interpretation.expert ?? "";

  const text = useMemo(() => {
    if (shouldReplaceReading(raw, locale)) {
      return composeReading({ he, patterns, persona }, locale);
    }
    return raw;
  }, [raw, locale, he, patterns, persona]);

  const recs = useMemo(() => {
    const fromApi = interpretation.recommendations ?? [];
    if (fromApi.length && !shouldReplaceReading(raw, locale)) {
      return fromApi.map((r) => (typeof r === "string" ? r : r.text ?? ""));
    }
    return composeRecommendations(patterns, locale);
  }, [interpretation.recommendations, patterns, locale, raw]);

  const disc = disclosure ?? {};
  const citations = (disc.retrieved_citation_ids ?? []).map(String);
  const needsReview = Boolean(interpretation.requires_human_review);

  return (
    <section data-testid="interpretation-region" aria-label={t("results.aiRegion")}>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 8,
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <AIDisclosureBadge
          model={disc.model ?? "rules-local"}
          limits={disc.limits || t("disclosure.limitsDefault")}
          citations={citations}
          reviewStatus={disc.review_status ?? "not_required"}
        />
        <PersonaToggle value={persona} onChange={setPersona} />
        {disc.degraded && (
          <span data-testid="degraded-banner" className="cs-badge cs-badge--trung">
            {t("disclosure.degraded")}
          </span>
        )}
      </div>

      {needsReview && (
        <div data-testid="human-review-slot" style={{ marginBottom: 12 }}>
          <HumanReviewGate riskLabel={t("review.pending")} />
        </div>
      )}

      <div data-testid="interpretation-text" className="cs-prose">
        {text}
      </div>

      {!!recs.length && (
        <ul data-testid="recommendations" style={{ marginTop: 16 }}>
          {recs.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      )}

      <div data-testid="citation-cards" style={{ marginTop: 16 }}>
        {(interpretation.citations ?? []).map((c, i) => (
          <CitationCard
            key={c.citation_id ?? i}
            citationId={c.citation_id}
            source={c.source}
            locator={c.locator}
            han={c.han ?? c.layers?.han}
            bachThoai={c.bach_thoai ?? c.layers?.vi ?? c.layers?.bach_thoai}
            dich={c.dich ?? c.layers?.en ?? c.layers?.dich}
          />
        ))}
      </div>
    </section>
  );
}
