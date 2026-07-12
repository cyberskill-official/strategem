"use client";

import { useState } from "react";
import { AIDisclosureBadge } from "../domain/ai-disclosure-badge";
import { PersonaToggle } from "../results/persona-toggle";
import type { StructuredReport } from "../../lib/api/report";
import { CitationList } from "./citation-list";
import { RecommendationsList } from "./recommendations-list";

/**
 * Interpreted region — AI reading with mandatory AIDisclosureBadge.
 * Persona toggle switches beginner/expert without re-fetch.
 */
export function InterpretationSection({
  report,
}: {
  report: StructuredReport;
}) {
  const [persona, setPersona] = useState<"beginner" | "expert">("beginner");
  const disc = report.ai_disclosure;
  const pending = disc.review_status === "pending";
  const text =
    persona === "beginner"
      ? report.interpretation.beginner
      : report.interpretation.expert;

  return (
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
      <div
        style={{
          display: "flex",
          gap: 12,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <h2 style={{ margin: 0 }}>Interpretation · AI</h2>
        <AIDisclosureBadge
          model={disc.model}
          limits={disc.limits}
          citations={report.citations.map((c) => c.source)}
          reviewStatus={disc.review_status}
        />
        {pending ? (
          <span
            data-testid="not-yet-approved"
            role="status"
            style={{
              background: "var(--color-warning, #f59e0b)",
              color: "#111",
              padding: "2px 8px",
              borderRadius: 4,
              fontSize: 12,
              fontWeight: 600,
            }}
          >
            Not yet approved
          </span>
        ) : null}
      </div>

      <PersonaToggle value={persona} onChange={setPersona} />

      <p data-testid="interpretation-text" style={{ whiteSpace: "pre-wrap" }}>
        {text}
      </p>

      <RecommendationsList items={report.interpretation.recommendations} />
      <CitationList citations={report.citations} />

      <p
        data-testid="confidence-supporting"
        style={{ fontSize: 13, opacity: 0.8 }}
      >
        Confidence (supporting context): {report.confidence.toFixed(2)}
      </p>
    </section>
  );
}
