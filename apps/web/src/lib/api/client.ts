import type { ApiError, QueryRequest, QueryResponse } from "./schemas";
import { validateQueryRequest } from "./schemas";

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

/** Browser uses same-origin /api (Next rewrite). Server can use absolute API_URL. */
export function apiBase(opts?: { baseUrl?: string }): string {
  if (opts?.baseUrl) return opts.baseUrl.replace(/\/$/, "");
  if (typeof window === "undefined") {
    return (process.env.API_URL || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000").replace(
      /\/$/,
      "",
    );
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
  return new ApiClientError(res.status, code, message, details);
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
  const res = await fetchFn(`${base}/api/v1/calculate/${system}`, {
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
      tier: "free",
    }),
  });
  if (!res.ok) throw await parseError(res);
  const data = (await res.json()) as QueryResponse;
  // client-side cache for immediate results navigation
  if (typeof window !== "undefined" && data.query_id) {
    try {
      sessionStorage.setItem(`query:${data.query_id}`, JSON.stringify(data));
    } catch {
      /* ignore quota */
    }
  }
  return data;
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
  if (opts?.token) headers.Authorization = `Bearer ${opts.token}`;

  // Prefer live API
  try {
    const res = await fetchFn(`${base}/api/v1/queries/${encodeURIComponent(queryId)}`, {
      method: "GET",
      headers,
      cache: "no-store",
    });
    if (res.ok) {
      return (await res.json()) as QueryResponse;
    }
    if (res.status !== 404) throw await parseError(res);
  } catch (e) {
    if (e instanceof ApiClientError) throw e;
    // network error — fall through to session cache
  }

  if (typeof window !== "undefined") {
    try {
      const raw = sessionStorage.getItem(`query:${queryId}`);
      if (raw) return JSON.parse(raw) as QueryResponse;
    } catch {
      /* ignore */
    }
  }
  throw new ApiClientError(404, "NOT_FOUND", `query ${queryId} not found`);
}
