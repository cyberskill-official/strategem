"use client";

import { useState } from "react";
import { cast, ApiClientError } from "../../lib/api/client";
import type { QueryRequest, QueryResponse } from "../../lib/api/schemas";
import {
  loadSchoolConfig,
  toCastPayloadFlags,
} from "../../lib/flags/school-flags";
import { Button } from "../ui/button";

const QUESTION_TYPES = [
  "trach_thoi",
  "hon_nhan",
  "tai_van",
  "suc_khoe",
  "khac",
];

export function QueryForm({
  system = "qimen",
  onSuccess,
}: {
  system?: string;
  onSuccess?: (queryId: string, response?: QueryResponse) => void;
}) {
  const [datetime, setDatetime] = useState("2004-01-01T10:30");
  const [tz, setTz] = useState("+07:00");
  const [place, setPlace] = useState("Ha Noi");
  const [kinhDo, setKinhDo] = useState("105.85");
  const [questionType, setQuestionType] = useState("trach_thoi");
  const [persona, setPersona] = useState<"beginner" | "expert">("beginner");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [castDisabled, setCastDisabled] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setFieldError(null);
    const school = loadSchoolConfig();
    const body: QueryRequest = {
      datetime: new Date(datetime).toISOString().slice(0, 19),
      tz,
      place,
      kinh_do: Number(kinhDo),
      question_type: questionType,
      systems: [system],
      persona_level: persona,
      co_truong_phai: toCastPayloadFlags(school),
    };
    setLoading(true);
    try {
      const res = await cast(system, body);
      onSuccess?.(res.query_id, res);
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (err.code === "VALIDATION_ERROR") setFieldError(err.message);
        else if (err.code === "FORBIDDEN_TIER")
          setError("This capability needs Premium or higher.");
        else if (err.code === "RATE_LIMITED") {
          setCastDisabled(true);
          const reset = err.details?.reset_at;
          setError(
            reset
              ? `Rate limited. Try again after ${String(reset)}.`
              : "Rate limited. Try later.",
          );
        } else setError(err.message || `API error (${err.status})`);
      } else setError("Unexpected error — is the API running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} style={{ display: "grid", gap: "var(--space-3)" }}>
      <p
        data-testid="disclaimer"
        style={{ fontSize: "var(--text-sm)", color: "var(--color-ink-muted)" }}
      >
        For cultural and educational use. Not medical, legal, or financial advice.
        AI output may be imperfect.
      </p>
      <label>
        Date & time
        <input
          type="datetime-local"
          value={datetime}
          onChange={(e) => setDatetime(e.target.value)}
          required
        />
      </label>
      <label>
        Timezone
        <input value={tz} onChange={(e) => setTz(e.target.value)} required />
      </label>
      <label>
        Place
        <input value={place} onChange={(e) => setPlace(e.target.value)} />
      </label>
      <label>
        Longitude
        <input
          value={kinhDo}
          onChange={(e) => setKinhDo(e.target.value)}
          inputMode="decimal"
        />
      </label>
      <label>
        Question type
        <select
          value={questionType}
          onChange={(e) => setQuestionType(e.target.value)}
        >
          {QUESTION_TYPES.map((q) => (
            <option key={q} value={q}>
              {q}
            </option>
          ))}
        </select>
      </label>
      <label>
        Persona
        <select
          value={persona}
          onChange={(e) => setPersona(e.target.value as "beginner" | "expert")}
        >
          <option value="beginner">beginner</option>
          <option value="expert">expert</option>
        </select>
      </label>
      {fieldError && (
        <p data-testid="field-error" style={{ color: "var(--color-danger)" }}>
          {fieldError}
        </p>
      )}
      {error && (
        <p data-testid="form-error" style={{ color: "var(--color-danger)" }}>
          {error}
        </p>
      )}
      <Button
        type="submit"
        disabled={loading || castDisabled}
        style={{ height: 44, width: "100%" }}
        data-testid="cast-button"
      >
        {loading ? "Casting…" : "Cast chart"}
      </Button>
    </form>
  );
}
