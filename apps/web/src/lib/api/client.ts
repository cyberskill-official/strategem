import type { ApiError, QueryRequest, QueryResponse } from "./schemas";
import { validateQueryRequest } from "./schemas";
import { getAccessToken } from "../auth/session";

export class ApiClientError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

/**
 * Browser: NEXT_PUBLIC_API_BASE (host-published API) or same-origin "" for rewrites.
 * Server: API_URL / API_INTERNAL_URL only — never NEXT_PUBLIC_* (breaks in Docker).
 */
export function apiBase(opts?: { baseUrl?: string }): string {
  if (opts?.baseUrl) return opts.baseUrl.replace(/\/$/, "");
  if (typeof window === "undefined") {
    return (
      process.env.API_URL ||
      process.env.API_INTERNAL_URL ||
      "http://127.0.0.1:8000"
    ).replace(/\/$/, "");
  }
  return (process.env.NEXT_PUBLIC_API_BASE || "").replace(/\/$/, "");
}

async function parseError(res: Response): Promise<ApiClientError> {
  let code = "INTERNAL";
  let message = res.statusText;
  let details: Record<string, unknown> | undefined;
  try {
    const j = (await res.json()) as ApiError;
    code = j.error?.code ?? code;
    message = j.error?.message ?? message;
    details = j.error?.details;
  } catch {
    /* ignore */
  }
  if (res.status === 429) code = "RATE_LIMITED";
  if (res.status === 403) code = "FORBIDDEN_TIER";
  return new ApiClientError(res.status, code, message, details);
}

const DEFAULT_TIMEOUT_MS = 25_000;

async function fetchWithTimeout(
  fetchFn: typeof fetch,
  input: string,
  init: RequestInit,
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<Response> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    return await fetchFn(input, { ...init, signal: ctrl.signal });
  } catch (e) {
    if (e instanceof Error && e.name === "AbortError") {
      throw new ApiClientError(0, "TIMEOUT", "request timed out");
    }
    throw new ApiClientError(0, "NETWORK", "network error");
  } finally {
    clearTimeout(timer);
  }
}

export async function cast(
  system: string,
  body: QueryRequest,
  opts?: { token?: string; baseUrl?: string; fetchImpl?: typeof fetch },
): Promise<QueryResponse> {
  const err = validateQueryRequest(body);
  if (err) {
    throw new ApiClientError(400, "VALIDATION_ERROR", err);
  }
  const base = apiBase(opts);
  const fetchFn = opts?.fetchImpl ?? fetch;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (opts?.token) headers.Authorization = `Bearer ${opts.token}`;
  const res = await fetchWithTimeout(fetchFn, `${base}/api/v1/calculate/${system}`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      datetime: body.datetime,
      tz: body.tz,
      place: body.place,
      kinh_do: body.kinh_do,
      longitude: body.kinh_do,
      question_type: body.question_type,
      systems: body.systems,
      persona_level: body.persona_level,
      co_truong_phai: body.co_truong_phai,
      question: body.question_type,
    }),
  });
  if (!res.ok) throw await parseError(res);
  const data = (await res.json()) as QueryResponse;
  // client-side cache for immediate results navigation
  if (typeof window !== "undefined" && data.query_id) {
    try {
      sessionStorage.setItem(
        `query:${data.query_id}`,
        JSON.stringify({ ...data, _place: body.place, _cast_at: body.datetime }),
      );
    } catch {
      /* ignore quota */
    }
  }
  return data;
}

export type FollowUpResponse = {
  query_id: string;
  message: string;
  answer: {
    beginner?: string;
    expert?: string;
    recommendations?: unknown[];
    citations?: Array<Record<string, unknown>>;
    confidence?: number;
    requires_human_review?: boolean;
  };
  ai_disclosure: {
    is_ai_generated?: boolean;
    model?: string;
    prompt_version?: string;
    retrieved_citation_ids?: string[];
    limits?: string;
    review_status?: "pending" | "not_required" | "approved" | "rejected";
    degraded?: boolean;
  };
  refused?: boolean;
  refuse_reason?: string | null;
};

/** Cited follow-up turn — POST /queries/{id}/follow-up (W6). */
export async function followUp(
  queryId: string,
  message: string,
  opts?: { locale?: string; token?: string; baseUrl?: string; fetchImpl?: typeof fetch },
): Promise<FollowUpResponse> {
  const base = apiBase(opts);
  const fetchFn = opts?.fetchImpl ?? fetch;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
  if (opts?.token) {
    headers.Authorization = `Bearer ${opts.token}`;
  } else {
    const t = getAccessToken();
    if (t) headers.Authorization = `Bearer ${t}`;
  }
  const res = await fetchWithTimeout(
    fetchFn,
    `${base}/api/v1/queries/${encodeURIComponent(queryId)}/follow-up`,
    {
      method: "POST",
      headers,
      body: JSON.stringify({
        message,
        locale: opts?.locale ?? "vi",
      }),
    },
  );
  if (!res.ok) throw await parseError(res);
  return (await res.json()) as FollowUpResponse;
}

export async function getQuery(
  queryId: string,
  opts?: { token?: string; baseUrl?: string; fetchImpl?: typeof fetch },
): Promise<QueryResponse> {
  const base = apiBase(opts);
  const fetchFn = opts?.fetchImpl ?? fetch;
  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  if (opts?.token) {
    headers.Authorization = `Bearer ${opts.token}`;
  } else {
    const t = getAccessToken();
    if (t) headers.Authorization = `Bearer ${t}`;
  }

  // Prefer live API
  try {
    const res = await fetchWithTimeout(
      fetchFn,
      `${base}/api/v1/queries/${encodeURIComponent(queryId)}`,
      { method: "GET", headers, cache: "no-store" },
    );
    if (res.ok) {
      return (await res.json()) as QueryResponse;
    }
    if (res.status !== 404) throw await parseError(res);
  } catch (e) {
    if (e instanceof ApiClientError && e.code !== "NETWORK" && e.code !== "TIMEOUT") {
      throw e;
    }
    // network / timeout — fall through to session cache
  }

  if (typeof window !== "undefined") {
    try {
      const raw = sessionStorage.getItem(`query:${queryId}`);
      if (raw) return JSON.parse(raw) as QueryResponse;
    } catch {
      /* ignore */
    }
  }

  // Demo / offline showcase boards
  if (queryId.startsWith("demo-") || queryId === "demo-ky-mon-showcase") {
    const { mockQueryResponse } = await import("../mock/fixtures");
    const demo = mockQueryResponse();
    return { ...demo, query_id: queryId };
  }

  throw new ApiClientError(404, "NOT_FOUND", `query ${queryId} not found`);
}
