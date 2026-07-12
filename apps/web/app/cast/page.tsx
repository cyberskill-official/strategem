"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { QueryForm } from "../../src/components/query/query-form";
import {
  ResultsPanel,
  type QueryResponseView,
} from "../../src/components/results/results-panel";
import type { QueryResponse } from "../../src/lib/api/schemas";

function toView(res: QueryResponse): QueryResponseView {
  return {
    query_id: res.query_id,
    charts: res.charts as QueryResponseView["charts"],
    patterns: (res.patterns || []) as QueryResponseView["patterns"],
    interpretation: res.interpretation as QueryResponseView["interpretation"],
    ai_disclosure: res.ai_disclosure as QueryResponseView["ai_disclosure"],
  };
}

export default function CastPage() {
  const router = useRouter();
  const [preview, setPreview] = useState<QueryResponseView | null>(null);

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(280px, 360px) 1fr",
        gap: "var(--space-5)",
        minHeight: "70vh",
      }}
    >
      <section aria-label="Query input">
        <h1 style={{ fontSize: "var(--text-xl)", marginBottom: "var(--space-4)" }}>
          New cast
        </h1>
        <QueryForm
          system="qimen"
          onSuccess={(queryId, full) => {
            if (full) setPreview(toView(full));
            router.push(`/results/${encodeURIComponent(queryId)}`);
          }}
        />
      </section>
      <section
        aria-label="Results"
        style={{
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-md)",
          padding: "var(--space-5)",
          color: "var(--color-ink-muted)",
        }}
      >
        {preview ? (
          <ResultsPanel response={preview} />
        ) : (
          <p>Cast a chart to see results here (live API).</p>
        )}
      </section>
    </div>
  );
}
