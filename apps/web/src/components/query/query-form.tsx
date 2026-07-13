"use client";

import { useState } from "react";
import { apiBase, cast, ApiClientError } from "../../lib/api/client";
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

type InputMode = "gregorian" | "lunar" | "bazi";

export function QueryForm({
  system = "qimen",
  onSuccess,
}: {
  system?: string;
  onSuccess?: (queryId: string, response?: QueryResponse) => void;
}) {
  const { t } = useLocale();
  const [inputMode, setInputMode] = useState<InputMode>("gregorian");
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
  // lunar
  const [lunarYear, setLunarYear] = useState("2003");
  const [lunarMonth, setLunarMonth] = useState("12");
  const [lunarDay, setLunarDay] = useState("10");
  const [lunarLeap, setLunarLeap] = useState(false);
  // bazi
  const [pillarNam, setPillarNam] = useState("癸未");
  const [pillarThang, setPillarThang] = useState("甲子");
  const [pillarNgay, setPillarNgay] = useState("戊午");
  const [pillarGio, setPillarGio] = useState("丁巳");

  async function resolveDatetime(): Promise<string> {
    if (inputMode === "gregorian") {
      return new Date(datetime).toISOString().slice(0, 19);
    }
    // COV-018: convert via CORE API — never invent calendar math in the browser
    const body =
      inputMode === "lunar"
        ? {
            input_mode: "lunar",
            lunar_year: Number(lunarYear),
            lunar_month: Number(lunarMonth),
            lunar_day: Number(lunarDay),
            leap: lunarLeap,
            hour: 12,
            tz,
            kinh_do: Number(kinhDo),
          }
        : {
            input_mode: "bazi",
            nam: pillarNam,
            thang: pillarThang,
            ngay: pillarNgay,
            gio: pillarGio,
            anchor_datetime: "2000-01-01T12:00:00",
            tz,
            kinh_do: Number(kinhDo),
          };
    const res = await fetch(`${apiBase()}/api/v1/calendar/convert`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg =
        data?.error?.message ||
        data?.error?.code ||
        t("cast.convertError");
      throw new ApiClientError(res.status, data?.error?.code || "VALIDATION_ERROR", msg);
    }
    if (!data.datetime) {
      throw new ApiClientError(400, "VALIDATION_ERROR", t("cast.convertError"));
    }
    return String(data.datetime).slice(0, 19);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setFieldError(null);
    const school = loadSchoolConfig();
    setLoading(true);
    try {
      const dt = await resolveDatetime();
      const body: QueryRequest = {
        datetime: dt,
        tz,
        place,
        kinh_do: Number(kinhDo),
        question_type: questionType,
        systems: [system],
        persona_level: persona,
        co_truong_phai: toCastPayloadFlags(school),
      };
      const res = await cast(system, body);
      onSuccess?.(res.query_id, res);
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (err.code === "VALIDATION_ERROR" || err.code?.includes("LUNAR") || err.code?.includes("PILLAR")) {
          setFieldError(err.message || t("error.validation"));
        } else if (err.code === "FORBIDDEN_TIER") setError(t("error.forbiddenTier"));
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

      {/* COV-018 input modes */}
      <fieldset className="cs-chip-field" data-testid="input-mode-field">
        <legend>{t("cast.inputMode")}</legend>
        <div className="cs-chip-row" role="radiogroup" aria-label={t("cast.inputMode")}>
          {(["gregorian", "lunar", "bazi"] as const).map((m) => (
            <button
              key={m}
              type="button"
              role="radio"
              aria-checked={inputMode === m}
              className={`cs-chip${inputMode === m ? " is-active" : ""}`}
              onClick={() => setInputMode(m)}
              data-testid={`input-mode-${m}`}
            >
              {t(`cast.mode.${m}`)}
            </button>
          ))}
        </div>
      </fieldset>

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

      {inputMode === "gregorian" ? (
        <label>
          {t("cast.datetime")}
          <input
            type="datetime-local"
            value={datetime}
            onChange={(e) => setDatetime(e.target.value)}
            required
            data-testid="cast-datetime"
          />
        </label>
      ) : null}

      {inputMode === "lunar" ? (
        <div className="cs-advanced-block" data-testid="lunar-fields">
          <label>
            {t("cast.lunarYear")}
            <input value={lunarYear} onChange={(e) => setLunarYear(e.target.value)} required inputMode="numeric" />
          </label>
          <label>
            {t("cast.lunarMonth")}
            <input value={lunarMonth} onChange={(e) => setLunarMonth(e.target.value)} required inputMode="numeric" />
          </label>
          <label>
            {t("cast.lunarDay")}
            <input value={lunarDay} onChange={(e) => setLunarDay(e.target.value)} required inputMode="numeric" />
          </label>
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={lunarLeap}
              onChange={(e) => setLunarLeap(e.target.checked)}
              data-testid="lunar-leap"
            />
            {t("cast.lunarLeap")}
          </label>
          <p className="cs-muted" style={{ fontSize: "0.85rem" }}>
            {t("cast.convertViaCore")}
          </p>
        </div>
      ) : null}

      {inputMode === "bazi" ? (
        <div className="cs-advanced-block" data-testid="bazi-fields">
          <label>
            {t("cast.pillarYear")}
            <input value={pillarNam} onChange={(e) => setPillarNam(e.target.value)} required data-testid="bazi-nam" />
          </label>
          <label>
            {t("cast.pillarMonth")}
            <input value={pillarThang} onChange={(e) => setPillarThang(e.target.value)} required />
          </label>
          <label>
            {t("cast.pillarDay")}
            <input value={pillarNgay} onChange={(e) => setPillarNgay(e.target.value)} required />
          </label>
          <label>
            {t("cast.pillarHour")}
            <input value={pillarGio} onChange={(e) => setPillarGio(e.target.value)} required />
          </label>
          <p className="cs-muted" style={{ fontSize: "0.85rem" }}>
            {t("cast.convertViaCore")}
          </p>
        </div>
      ) : null}

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
