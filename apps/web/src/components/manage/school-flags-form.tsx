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
import { displayOption } from "../../lib/domain/glossary";
import { useLocale } from "../i18n/locale-provider";
import { Button } from "../ui/button";

const GROUP_ORDER = ["ky_mon", "luc_nham", "thai_at", "shared"] as const;

export function SchoolFlagsForm({
  onChange,
}: {
  onChange?: (cfg: SchoolConfig) => void;
}) {
  const { t, locale } = useLocale();
  const [cfg, setCfg] = useState<SchoolConfig>(defaultSchoolConfig);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const loaded = loadSchoolConfig();
    setCfg(loaded);
    onChange?.(loaded);
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

      {GROUP_ORDER.map((group) => {
        const flags = SCHOOL_FLAGS.filter((f) => f.system === group);
        if (!flags.length) return null;
        return (
          <fieldset
            key={group}
            style={{
              border: "1px solid var(--cs-color-border-default)",
              borderRadius: 12,
              padding: 16,
              marginBottom: 16,
            }}
          >
            <legend style={{ fontWeight: 700, padding: "0 8px" }}>
              {t(`settings.group.${group}`)}
            </legend>
            {flags.map((f) => {
              const value =
                f.system === "shared"
                  ? cfg.co_lich_phap[f.key]
                  : cfg.co_truong_phai[`${f.system}.${f.key}`];
              return (
                <label
                  key={`${f.system}-${f.key}`}
                  style={{ display: "block", marginBottom: 14 }}
                >
                  <span style={{ fontWeight: 600 }}>
                    {t(`settings.flag.${f.key}`)}{" "}
                    <em className="cs-muted" style={{ fontWeight: 400 }}>
                      ({t("settings.default")}: {displayOption(f.default, locale)})
                    </em>
                  </span>
                  <select
                    data-testid={`flag-${f.key}`}
                    value={value}
                    onChange={(e) => setFlag(f.system, f.key, e.target.value)}
                  >
                    {f.options.map((o) => (
                      <option key={o} value={o}>
                        {displayOption(o, locale)}
                        {o === f.default ? ` (${t("settings.default")})` : ""}
                      </option>
                    ))}
                  </select>
                  <span className="cs-muted" style={{ display: "block", marginTop: 4 }}>
                    {t(`settings.desc.${f.key}`)}
                  </span>
                </label>
              );
            })}
          </fieldset>
        );
      })}

      <Button
        type="button"
        data-testid="save-school-flags"
        onClick={persist}
        style={{ marginTop: 4 }}
      >
        {t("settings.save")}
      </Button>
      {saved ? (
        <p data-testid="school-flags-saved" className="cs-muted" style={{ marginTop: 8 }}>
          {t("settings.saved")}
        </p>
      ) : null}
      <details style={{ marginTop: 16 }}>
        <summary className="cs-muted" style={{ cursor: "pointer" }}>
          {t("settings.payload")}
        </summary>
        <pre
          data-testid="cast-overrides"
          style={{
            marginTop: 8,
            padding: 12,
            background: "var(--cs-color-surface-raised)",
            borderRadius: 8,
            fontSize: 12,
            overflow: "auto",
          }}
        >
          {JSON.stringify(toCastOverrides(cfg), null, 2)}
        </pre>
      </details>
    </form>
  );
}
