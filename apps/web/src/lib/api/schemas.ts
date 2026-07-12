/** FR-WEB-002 / FR-API-001 request+response shapes (manual mirror; zod optional). */

export type QueryRequest = {
  datetime: string;
  tz: string;
  place?: string;
  kinh_do?: number;
  question_type: string;
  systems: string[];
  persona_level?: "beginner" | "expert";
  co_truong_phai?: Record<string, string>;
};

export type ApiError = {
  error: {
    code: string;
    message: string;
    request_id?: string;
    details?: Record<string, unknown>;
  };
};

export type QueryResponse = {
  query_id: string;
  charts: Record<string, unknown>;
  patterns: unknown[];
  interpretation?: unknown;
  ai_disclosure?: unknown;
};

export function validateQueryRequest(body: QueryRequest): string | null {
  if (!body.datetime) return "datetime required";
  if (!body.tz) return "tz required";
  if (!body.question_type) return "question_type required";
  if (!body.systems?.length) return "systems required";
  return null;
}
