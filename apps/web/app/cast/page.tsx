"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
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
  const { t } = useLocale();
  const [preview, setPreview] = useState<QueryResponseView | null>(null);

  return (
    <div className="cs-page cs-grid-2" style={{ minHeight: "70vh" }}>
      <section className="cs-card" aria-label={t("cast.title")}>
        <h1>{t("cast.title")}</h1>
        <p className="cs-muted">{t("cast.subtitle")}</p>
        <QueryForm
          system="qimen"
          onSuccess={(queryId, full) => {
            if (full) setPreview(toView(full));
            router.push(`/results/${encodeURIComponent(queryId)}`);
          }}
        />
      </section>
      <section
        className="cs-region"
        aria-label={t("nav.results")}
        style={{ color: "var(--color-ink-muted)" }}
      >
        {preview ? (
          <ResultsPanel response={preview} />
        ) : (
          <p>{t("cast.resultsEmpty")}</p>
        )}
      </section>
    </div>
  );
}
