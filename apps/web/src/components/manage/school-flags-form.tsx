"use client";

import { useEffect, useState } from "react";
import {
  SCHOOL_FLAGS,
  defaultSchoolConfig,
  loadSchoolConfig,
  saveSchoolConfig,
  toCastOverrides,
  type SchoolConfig,
} from "../../lib/flags/school-flags";
import { useLocale } from "../i18n/locale-provider";
import { Button } from "../ui/button";

/**
 * School flag form — enums with defaults; never marks a school "correct".
 * Sets flags only; does not cast. Persists to localStorage for cast payload.
 */
export function SchoolFlagsForm({
  onChange,
}: {
  onChange?: (cfg: SchoolConfig) => void;
}) {
  const { t } = useLocale();
  const [cfg, setCfg] = useState<SchoolConfig>(defaultSchoolConfig);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const loaded = loadSchoolConfig();
    setCfg(loaded);
    onChange?.(loaded);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- load once
  }, []);

  const setFlag = (system: string, key: string, value: string) => {
    setCfg((prev) => {
      const next: SchoolConfig = {
        co_truong_phai: { ...prev.co_truong_phai },
        co_lich_phap: { ...prev.co_lich_phap },
      };
      if (system === "shared") next.co_lich_phap[key] = value;
      else next.co_truong_phai[`${system}.${key}`] = value;
      onChange?.(next);
      return next;
    });
    setSaved(false);
  };

  const persist = () => {
    saveSchoolConfig(cfg);
    setSaved(true);
  };

  return (
    <form data-testid="school-flags-form" onSubmit={(e) => e.preventDefault()}>
      <p data-testid="fairness-note" className="cs-disclaimer">
        {t("settings.fairness")}
      </p>
      {SCHOOL_FLAGS.map((f) => {
        const value =
          f.system === "shared"
            ? cfg.co_lich_phap[f.key]
            : cfg.co_truong_phai[`${f.system}.${f.key}`];
        return (
          <label
            key={`${f.system}-${f.key}`}
            style={{ display: "block", marginBottom: 12 }}
          >
            <span>
              {f.system}.{f.key}{" "}
              <em>
                ({t("settings.default")}: {f.default})
              </em>
            </span>
            <select
              data-testid={`flag-${f.key}`}
              value={value}
              onChange={(e) => setFlag(f.system, f.key, e.target.value)}
            >
              {f.options.map((o) => (
                <option key={o} value={o}>
                  {o}
                  {o === f.default ? ` (${t("settings.default")})` : ""}
                </option>
              ))}
            </select>
            <span className="cs-muted" style={{ display: "block" }}>
              {f.description}
            </span>
          </label>
        );
      })}
      <Button
        type="button"
        data-testid="save-school-flags"
        onClick={persist}
        style={{ marginTop: 8 }}
      >
        {t("settings.save")}
      </Button>
      {saved ? (
        <p data-testid="school-flags-saved" className="cs-muted" style={{ marginTop: 8 }}>
          {t("settings.saved")}
        </p>
      ) : null}
      <pre
        data-testid="cast-overrides"
        style={{
          marginTop: 16,
          padding: 12,
          background: "var(--cs-color-surface-raised)",
          borderRadius: 8,
          fontSize: 12,
          overflow: "auto",
        }}
      >
        {JSON.stringify(toCastOverrides(cfg), null, 2)}
      </pre>
    </form>
  );
}
