"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
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

/** Live results — loads from API / session cache. No demo fixtures. */
export default function ResultsPage() {
  const params = useParams();
  const queryId = String(params?.queryId ?? "");
  const [response, setResponse] = useState<QueryResponseView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!queryId) {
        setError("missing query id");
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const res = await getQuery(queryId);
        if (!cancelled) setResponse(toView(res));
      } catch (e) {
        if (!cancelled) {
          setError(
            e instanceof ApiClientError
              ? e.message
              : "Failed to load query — cast again from /cast",
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
  }, [queryId]);

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: 16 }}>
      <h1 style={{ fontSize: "var(--text-xl)" }}>Results · {queryId}</h1>
      {loading && <p data-testid="results-loading">Loading…</p>}
      {error && (
        <p data-testid="results-error" style={{ color: "var(--color-danger)" }}>
          {error}
        </p>
      )}
      {response && !loading ? <ResultsPanel response={response} /> : null}
    </div>
  );
}
