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
  const [showAdvanced, setShowAdvanced] = useState(false);
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
        if (err.code === "VALIDATION_ERROR") setFieldError(t("error.validation"));
        else if (err.code === "FORBIDDEN_TIER") setError(t("error.forbiddenTier"));
        else if (err.code === "RATE_LIMITED") {
          setCastDisabled(true);
          setError(t("error.rateLimited"));
        } else if (err.code === "TIMEOUT") setError(t("error.timeout"));
        else if (err.code === "NETWORK") setError(t("error.apiDown"));
        else setError(err.message || t("error.generic"));
      } else setError(t("cast.apiError"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="cs-query-form">
      <p className="cs-query-form__title">{t("cast.formTitle")}</p>

      <fieldset className="cs-chip-field">
        <legend>{t("cast.questionType")}</legend>
        <div className="cs-chip-row" role="radiogroup" aria-label={t("cast.questionType")}>
          {QUESTION_TYPES.map((q) => {
            const active = questionType === q;
            return (
              <button
                key={q}
                type="button"
                role="radio"
                aria-checked={active}
                className={`cs-chip${active ? " is-active" : ""}`}
                onClick={() => setQuestionType(q)}
                data-testid={`qtype-${q}`}
              >
                {t(`cast.q.${q}`)}
              </button>
            );
          })}
        </div>
      </fieldset>

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
        {t("cast.place")}
        <input value={place} onChange={(e) => setPlace(e.target.value)} />
      </label>

      <fieldset className="cs-chip-field">
        <legend>{t("cast.persona")}</legend>
        <div className="cs-chip-row" role="radiogroup">
          {(["beginner", "expert"] as const).map((p) => (
            <button
              key={p}
              type="button"
              role="radio"
              aria-checked={persona === p}
              className={`cs-chip${persona === p ? " is-active" : ""}`}
              onClick={() => setPersona(p)}
            >
              {t(`cast.persona.${p}`)}
            </button>
          ))}
        </div>
      </fieldset>

      <button
        type="button"
        className="cs-advanced-toggle"
        aria-expanded={showAdvanced}
        onClick={() => setShowAdvanced((v) => !v)}
      >
        {showAdvanced ? "▾ " : "▸ "}
        {t("cast.advanced")}
      </button>

      {showAdvanced ? (
        <div className="cs-advanced-block">
          <label>
            {t("cast.timezone")}
            <input value={tz} onChange={(e) => setTz(e.target.value)} required />
          </label>
          <label>
            {t("cast.longitude")}
            <input
              value={kinhDo}
              onChange={(e) => setKinhDo(e.target.value)}
              inputMode="decimal"
            />
          </label>
        </div>
      ) : null}

      <p data-testid="disclaimer" className="cs-disclaimer">
        {t("disclaimer.short")}
      </p>

      {fieldError && (
        <p data-testid="field-error" className="cs-error-banner">
          {fieldError}
        </p>
      )}
      {error && (
        <p data-testid="form-error" className="cs-error-banner">
          {error}
        </p>
      )}
      {loading ? (
        <div className="cs-skeleton" data-testid="cast-loading">
          <div className="cs-skeleton__bar" />
          <div className="cs-skeleton__bar cs-skeleton__bar--short" />
          <p className="cs-muted">{t("cast.skeleton")}</p>
          <p className="cs-muted">{t("cast.loadingHint")}</p>
        </div>
      ) : null}
      <Button
        type="submit"
        disabled={loading || castDisabled}
        className="cs-link-btn--pulse"
        style={{ height: 48, width: "100%" }}
        data-testid="cast-button"
      >
        {loading ? t("cast.loading") : t("cast.button")}
      </Button>
    </form>
  );
}
