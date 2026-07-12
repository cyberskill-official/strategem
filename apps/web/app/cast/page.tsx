"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { QueryForm } from "../../src/components/query/query-form";
import {
  ResultsPanel,
  type QueryResponseView,
} from "../../src/components/results/results-panel";
import type { QueryResponse } from "../../src/lib/api/schemas";

const SYSTEMS = [
  { id: "qimen", key: "system.qimen", blurb: "system.qimen.blurb", glyph: "奇" },
  { id: "liuren", key: "system.liuren", blurb: "system.liuren.blurb", glyph: "壬" },
  { id: "taiyi", key: "system.taiyi", blurb: "system.taiyi.blurb", glyph: "乙" },
] as const;

function toView(res: QueryResponse): QueryResponseView {
  return {
    query_id: res.query_id,
    charts: res.charts as QueryResponseView["charts"],
    patterns: (res.patterns || []) as QueryResponseView["patterns"],
    interpretation: res.interpretation as QueryResponseView["interpretation"],
    ai_disclosure: res.ai_disclosure as QueryResponseView["ai_disclosure"],
  };
}

function CastInner() {
  const router = useRouter();
  const params = useSearchParams();
  const { t } = useLocale();
  const initial = useMemo(() => {
    const s = params.get("system");
    if (s === "liuren" || s === "taiyi" || s === "qimen") return s;
    return "qimen";
  }, [params]);
  const [system, setSystem] = useState(initial);
  const [preview, setPreview] = useState<QueryResponseView | null>(null);

  return (
    <div className="cs-page cs-reveal">
      <header>
        <p className="cs-kicker">{t("cast.system")}</p>
        <h1>{t("cast.title")}</h1>
        <p className="cs-muted" style={{ maxWidth: "52ch" }}>
          {t("cast.subtitle")}
        </p>
      </header>

      <div id="systems" className="cs-grid-3">
        {SYSTEMS.map((s) => (
          <button
            key={s.id}
            type="button"
            className={`cs-system-tile${system === s.id ? " is-active" : ""}`}
            aria-pressed={system === s.id}
            onClick={() => setSystem(s.id)}
          >
            <div className="cs-system-tile__glyph" aria-hidden>
              {s.glyph}
            </div>
            <div style={{ fontWeight: 700 }}>{t(s.key)}</div>
            <div className="cs-muted" style={{ marginTop: 4 }}>
              {t(s.blurb)}
            </div>
          </button>
        ))}
      </div>

      <div className="cs-grid-2" style={{ minHeight: "60vh" }}>
        <section className="cs-card" aria-label={t("cast.title")}>
          <QueryForm
            system={system}
            onSuccess={(queryId, full) => {
              if (full) setPreview(toView(full));
              router.push(`/results/${encodeURIComponent(queryId)}`);
            }}
          />
        </section>
        <section className="cs-region" aria-label={t("nav.results")}>
          {preview ? (
            <ResultsPanel response={preview} />
          ) : (
            <div className="cs-empty" data-testid="cast-results-empty">
              <div className="cs-empty__title">{t("cast.resultsEmptyTitle")}</div>
              <p style={{ margin: 0 }}>{t("cast.resultsEmpty")}</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default function CastPage() {
  return (
    <Suspense fallback={null}>
      <CastInner />
    </Suspense>
  );
}
