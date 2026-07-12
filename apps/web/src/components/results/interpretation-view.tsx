"use client";

import { useState } from "react";
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
}: {
  interpretation: InterpretationData;
  disclosure?: DisclosureData | null;
}) {
  const [persona, setPersona] = useState<Persona>("beginner");
  const text =
    persona === "expert"
      ? interpretation.expert ?? interpretation.beginner ?? ""
      : interpretation.beginner ?? interpretation.expert ?? "";

  const disc = disclosure ?? {};
  const citations = (disc.retrieved_citation_ids ?? []).map(String);
  const needsReview = Boolean(interpretation.requires_human_review);

  return (
    <section data-testid="interpretation-region" aria-label="AI interpretation">
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
          model={disc.model ?? "unknown"}
          limits={disc.limits ?? "Educational use only."}
          citations={citations}
          reviewStatus={disc.review_status ?? "not_required"}
        />
        <PersonaToggle value={persona} onChange={setPersona} />
        {disc.degraded && (
          <span data-testid="degraded-banner" style={{ fontSize: 12 }}>
            Degraded (rule-based) reading
          </span>
        )}
      </div>

      {needsReview && (
        <div data-testid="human-review-slot" style={{ marginBottom: 12 }}>
          <HumanReviewGate riskLabel="Pending human review — not yet approved for decision use." />
        </div>
      )}

      <div data-testid="interpretation-text" style={{ whiteSpace: "pre-wrap" }}>
        {text}
      </div>

      {!!interpretation.recommendations?.length && (
        <ul data-testid="recommendations">
          {interpretation.recommendations.map((r, i) => (
            <li key={i}>{typeof r === "string" ? r : r.text ?? ""}</li>
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
