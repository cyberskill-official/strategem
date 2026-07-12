"use client";

import { useState } from "react";
import { cast, ApiClientError } from "../../lib/api/client";
import type { QueryRequest, QueryResponse } from "../../lib/api/schemas";
import {
  loadSchoolConfig,
  toCastPayloadFlags,
} from "../../lib/flags/school-flags";
import { useLocale } from "../i18n/locale-provider";
import { Button } from "../ui/button";

const QUESTION_TYPES = [
  "trach_thoi",
  "hon_nhan",
  "tai_van",
  "suc_khoe",
  "khac",
] as const;

export function QueryForm({
  system = "qimen",
  onSuccess,
}: {
  system?: string;
  onSuccess?: (queryId: string, response?: QueryResponse) => void;
}) {
  const { t } = useLocale();
  const [datetime, setDatetime] = useState("2004-01-01T10:30");
  const [tz, setTz] = useState("+07:00");
  const [place, setPlace] = useState("Hà Nội");
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
          setError(t("error.forbiddenTier"));
        else if (err.code === "RATE_LIMITED") {
          setCastDisabled(true);
          const reset = err.details?.reset_at;
          setError(
            reset
              ? t("error.rateLimitedUntil", { reset: String(reset) })
              : t("error.rateLimited"),
          );
        } else setError(err.message || t("error.generic"));
      } else setError(t("cast.apiError"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} style={{ display: "grid", gap: "var(--space-3)" }}>
      <p data-testid="disclaimer" className="cs-disclaimer">
        {t("disclaimer.full")}
      </p>
      <label>
        {t("cast.datetime")}
        <input
          type="datetime-local"
          value={datetime}
          onChange={(e) => setDatetime(e.target.value)}
          required
        />
      </label>
      <label>
        {t("cast.timezone")}
        <input value={tz} onChange={(e) => setTz(e.target.value)} required />
      </label>
      <label>
        {t("cast.place")}
        <input value={place} onChange={(e) => setPlace(e.target.value)} />
      </label>
      <label>
        {t("cast.longitude")}
        <input
          value={kinhDo}
          onChange={(e) => setKinhDo(e.target.value)}
          inputMode="decimal"
        />
      </label>
      <label>
        {t("cast.questionType")}
        <select
          value={questionType}
          onChange={(e) => setQuestionType(e.target.value)}
        >
          {QUESTION_TYPES.map((q) => (
            <option key={q} value={q}>
              {t(`cast.q.${q}`)}
            </option>
          ))}
        </select>
      </label>
      <label>
        {t("cast.persona")}
        <select
          value={persona}
          onChange={(e) => setPersona(e.target.value as "beginner" | "expert")}
        >
          <option value="beginner">{t("cast.persona.beginner")}</option>
          <option value="expert">{t("cast.persona.expert")}</option>
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
        {loading ? t("cast.loading") : t("cast.button")}
      </Button>
    </form>
  );
}
