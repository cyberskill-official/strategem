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

function toView(
  res: QueryResponse,
  extra?: Partial<QueryResponseView>,
): QueryResponseView {
  return {
    query_id: res.query_id,
    charts: res.charts as QueryResponseView["charts"],
    patterns: (res.patterns || []) as QueryResponseView["patterns"],
    interpretation: res.interpretation as QueryResponseView["interpretation"],
    ai_disclosure: res.ai_disclosure as QueryResponseView["ai_disclosure"],
    ...extra,
  };
}

function formatWhen(iso: string, locale: string): string {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso.slice(0, 16).replace("T", " ");
    return new Intl.DateTimeFormat(locale === "zh" ? "zh-CN" : locale === "en" ? "en-GB" : "vi-VN", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(d);
  } catch {
    return iso.slice(0, 16);
  }
}

export default function ResultsPage() {
  const params = useParams();
  const queryId = String(params?.queryId ?? "");
  const { t, locale } = useLocale();
  const [response, setResponse] = useState<QueryResponseView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [reportId, setReportId] = useState<string | undefined>();
  const [meta, setMeta] = useState({
    he: "ky_mon",
    question_type: "trach_thoi",
    cast_at: "",
    place: "",
  });

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
          const first = Object.values(res.charts ?? {})[0] as
            | { he?: string; ban?: { place?: string } }
            | undefined;
          const he = first?.he ?? "ky_mon";
          const isDemo = queryId.startsWith("demo-");
          setResponse(
            toView(res, {
              engine_mode: isDemo ? "demo" : "cast_cli",
              place: meta.place || "Hà Nội",
              cast_at: meta.cast_at,
            }),
          );
          setMeta((m) => ({
            ...m,
            he,
            cast_at: m.cast_at || new Date().toISOString(),
          }));
          try {
            const { getHistory } = await import("../../../src/lib/api/history");
            const hist = await getHistory();
            const hit = hist.items.find((i) => i.query_id === queryId);
            if (hit) {
              setReportId(hit.report_id);
              setMeta((prev) => ({
                he: hit.he,
                question_type: hit.question_type,
                cast_at: hit.created_at,
                place: prev.place || "Hà Nội",
              }));
              setResponse((prev) =>
                prev
                  ? {
                      ...prev,
                      cast_at: hit.created_at,
                      place: prev.place || "Hà Nội",
                    }
                  : prev,
              );
            }
          } catch {
            /* ignore */
          }
        }
      } catch (e) {
        if (!cancelled) {
          if (e instanceof ApiClientError) {
            if (e.code === "RATE_LIMITED") setError(t("error.rateLimited"));
            else if (e.status === 0 || e.code === "NETWORK") setError(t("error.apiDown"));
            else if (e.code === "TIMEOUT") setError(t("error.timeout"));
            else setError(e.message || t("results.error"));
          } else setError(t("results.error"));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- load once per queryId
  }, [queryId, t]);

  const systemLabel = (() => {
    const key = `system.${meta.he}`;
    const label = t(key);
    return label.startsWith("[missing:") ? meta.he : label;
  })();

  return (
    <div className="cs-page cs-reveal">
      <header className="cs-results-header">
        <p className="cs-kicker">{t("nav.results")}</p>
        <h1>{t("results.title")}</h1>
        <p className="cs-results-meta" data-testid="results-meta">
          <span>
            {t("results.meta.when", {
              when: formatWhen(meta.cast_at || new Date().toISOString(), locale),
            })}
          </span>
          <span aria-hidden>·</span>
          <span>
            {t("results.meta.place", { place: meta.place || "Hà Nội" })}
          </span>
          <span aria-hidden>·</span>
          <span>{t("results.meta.system", { system: systemLabel })}</span>
        </p>
        <div className="cs-results-actions">
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
            >
              {t("results.openReport")}
            </Link>
          ) : null}
          <Link href="/cast" className="cs-link-btn cs-link-btn--primary">
            {t("cast.button")}
          </Link>
        </div>
      </header>

      {loading ? (
        <div className="cs-skeleton" data-testid="results-loading">
          <div className="cs-skeleton__bar" />
          <div className="cs-skeleton__bar cs-skeleton__bar--short" />
          <p className="cs-muted">{t("results.loading")}</p>
        </div>
      ) : null}
      {error ? (
        <p data-testid="results-error" className="cs-error-banner">
          {error}
        </p>
      ) : null}
      {response && !loading ? <ResultsPanel response={response} /> : null}
    </div>
  );
}
