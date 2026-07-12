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

export async function cast(
  system: string,
  body: QueryRequest,
  opts?: { token?: string; baseUrl?: string; fetchImpl?: typeof fetch },
): Promise<QueryResponse> {
  const err = validateQueryRequest(body);
  if (err) {
    throw new ApiClientError(400, "VALIDATION_ERROR", err);
  }
  const base = opts?.baseUrl ?? "";
  const fetchFn = opts?.fetchImpl ?? fetch;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (opts?.token) headers.Authorization = `Bearer ${opts.token}`;
  const res = await fetchFn(`${base}/api/v1/calculate/${system}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
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
    throw new ApiClientError(res.status, code, message, details);
  }
  return (await res.json()) as QueryResponse;
}
