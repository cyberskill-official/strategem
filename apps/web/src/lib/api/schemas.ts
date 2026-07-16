/** TASK-WEB-002 / TASK-API-001 request+response shapes (manual mirror; zod optional). */

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

export type PatternItem = {
  id?: string;
  name?: string;
  cung?: number | null;
  polarity?: "cat" | "hung" | "trung" | string;
  score?: number | null;
  citations?: string[];
};

export type InterpretationPayload = {
  beginner?: string;
  expert?: string;
  recommendations?: Array<string | { text?: string; citations?: string[] }>;
  citations?: Array<{
    citation_id?: string;
    source?: string;
    locator?: string;
    layers?: Record<string, string>;
    han?: string;
    bach_thoai?: string;
    dich?: string;
  }>;
  requires_human_review?: boolean;
  confidence?: number;
};

export type AiDisclosurePayload = {
  is_ai_generated?: boolean;
  model?: string;
  prompt_version?: string;
  retrieved_citation_ids?: string[];
  limits?: string;
  review_status?: "pending" | "not_required" | "approved" | "rejected";
  degraded?: boolean;
};

export type ChartEnvelope = {
  envelope_version?: number;
  he?: string;
  ban?: Record<string, unknown>;
  cach_cuc?: PatternItem[];
  lich_phap?: Record<string, unknown>;
  provenance?: Record<string, unknown>;
  [key: string]: unknown;
};

export type QueryResponse = {
  query_id: string;
  charts: Record<string, ChartEnvelope>;
  patterns: PatternItem[];
  interpretation?: InterpretationPayload | null;
  ai_disclosure?: AiDisclosurePayload | null;
};

export function validateQueryRequest(body: QueryRequest): string | null {
  if (!body.datetime) return "datetime required";
  if (!body.tz) return "tz required";
  if (!body.question_type) return "question_type required";
  if (!body.systems?.length) return "systems required";
  return null;
}
