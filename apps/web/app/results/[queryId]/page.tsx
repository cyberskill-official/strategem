"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useLocale } from "../../../src/components/i18n/locale-provider";
import { PinButton } from "../../../src/components/results/pin-button";
import { getQuery, ApiClientError } from "../../../src/lib/api/client";
import {
  ResultsPanel,
  type QueryResponseView,
} from "../../../src/components/results/results-panel";
import type { QueryResponse } from "../../../src/lib/api/schemas";

function toView(res: QueryResponse): QueryResponseView {
  return {
    query_id: res.query_id,
    charts: res.charts as QueryResponseView["charts"],
    patterns: (res.patterns || []) as QueryResponseView["patterns"],
    interpretation: res.interpretation as QueryResponseView["interpretation"],
    ai_disclosure: res.ai_disclosure as QueryResponseView["ai_disclosure"],
  };
}

export default function ResultsPage() {
  const params = useParams();
  const queryId = String(params?.queryId ?? "");
  const { t } = useLocale();
  const [response, setResponse] = useState<QueryResponseView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [reportId, setReportId] = useState<string | undefined>();
  const [meta, setMeta] = useState({ he: "ky_mon", question_type: "trach_thoi", cast_at: "" });

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!queryId) {
        setError(t("results.error"));
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const res = await getQuery(queryId);
        if (!cancelled) {
          setResponse(toView(res));
          const first = Object.values(res.charts ?? {})[0] as
            | { he?: string }
            | undefined;
          setMeta((m) => ({
            ...m,
            he: first?.he ?? m.he,
            cast_at: new Date().toISOString(),
          }));
          try {
            const { getHistory } = await import("../../../src/lib/api/history");
            const hist = await getHistory();
            const hit = hist.items.find((i) => i.query_id === queryId);
            if (hit) {
              setReportId(hit.report_id);
              setMeta({
                he: hit.he,
                question_type: hit.question_type,
                cast_at: hit.created_at,
              });
            }
          } catch {
            /* ignore */
          }
        }
      } catch (e) {
        if (!cancelled) {
          setError(
            e instanceof ApiClientError ? e.message : t("results.error"),
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [queryId, t]);

  return (
    <div className="cs-page cs-reveal">
      <header style={{ display: "grid", gap: 8 }}>
        <p className="cs-kicker">{t("nav.results")}</p>
        <h1 style={{ marginBottom: 0 }}>{t("results.title")}</h1>
        {queryId ? (
          <p
            className="cs-muted"
            style={{ margin: 0, fontFamily: "ui-monospace, monospace", fontSize: 12 }}
          >
            {queryId}
          </p>
        ) : null}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 4 }}>
          {queryId ? (
            <PinButton
              queryId={queryId}
              he={meta.he}
              questionType={meta.question_type}
              castAt={meta.cast_at}
              reportId={reportId}
            />
          ) : null}
          {reportId ? (
            <Link
              href={`/report/${encodeURIComponent(reportId)}`}
              className="cs-link-btn cs-link-btn--secondary"
              style={{ minHeight: 40, padding: "0 14px" }}
            >
              {t("results.openReport")}
            </Link>
          ) : null}
          <Link
            href="/cast"
            className="cs-link-btn cs-link-btn--primary"
            style={{ minHeight: 40, padding: "0 14px" }}
          >
            {t("cast.button")}
          </Link>
        </div>
      </header>
      {loading && <p data-testid="results-loading">{t("results.loading")}</p>}
      {error && (
        <p data-testid="results-error" style={{ color: "var(--color-danger)" }}>
          {error}
        </p>
      )}
      {response && !loading ? <ResultsPanel response={response} /> : null}
    </div>
  );
}
