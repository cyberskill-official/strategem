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
import {
  IconCompass,
  IconDialogue,
  IconMap,
  IconSeasons,
} from "../../src/components/visual/story-icons";

const SYSTEMS = [
  {
    id: "qimen",
    plain: "system.qimen.plain",
    blurb: "system.qimen.blurb",
    name: "system.qimen",
    Icon: IconCompass,
  },
  {
    id: "liuren",
    plain: "system.liuren.plain",
    blurb: "system.liuren.blurb",
    name: "system.liuren",
    Icon: IconDialogue,
  },
  {
    id: "taiyi",
    plain: "system.taiyi.plain",
    blurb: "system.taiyi.blurb",
    name: "system.taiyi",
    Icon: IconSeasons,
  },
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
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("cast.system")}</p>
        <h1>{t("cast.title")}</h1>
        <p className="cs-lead-short">{t("cast.subtitle")}</p>
      </header>

      <div id="systems" className="cs-grid-3 cs-stagger">
        {SYSTEMS.map((s) => (
          <button
            key={s.id}
            type="button"
            className={`cs-visual-card cs-visual-card--door${system === s.id ? " is-active" : ""}`}
            aria-pressed={system === s.id}
            onClick={() => setSystem(s.id)}
          >
            <s.Icon className="cs-icon" />
            <h3>{t(s.plain)}</h3>
            <p>{t(s.blurb)}</p>
            <span className="cs-visual-card__tag">{t(s.name)}</span>
          </button>
        ))}
      </div>

      <p className="cs-hint-pill" role="note">
        {t("cast.hint")}
      </p>

      <div className="cs-grid-2">
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
            <div className="cs-empty cs-empty--visual" data-testid="cast-results-empty">
              <IconMap className="cs-icon cs-icon--lg" />
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
