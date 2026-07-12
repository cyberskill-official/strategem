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

/**
 * School flag form — enums with defaults; never marks a school "correct".
 * Sets flags only; does not cast. Persists to localStorage for cast payload.
 */
export function SchoolFlagsForm({
  onChange,
}: {
  onChange?: (cfg: SchoolConfig) => void;
}) {
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
      <p data-testid="fairness-note">
        Each school option is listed with its default. No school is marked
        correct.
      </p>
      {SCHOOL_FLAGS.map((f) => {
        const value =
          f.system === "shared"
            ? cfg.co_lich_phap[f.key]
            : cfg.co_truong_phai[`${f.system}.${f.key}`];
        return (
          <label
            key={`${f.system}-${f.key}`}
            style={{ display: "block", marginBottom: 8 }}
          >
            <span>
              {f.system}.{f.key} <em>(default: {f.default})</em>
            </span>
            <select
              data-testid={`flag-${f.key}`}
              value={value}
              onChange={(e) => setFlag(f.system, f.key, e.target.value)}
            >
              {f.options.map((o) => (
                <option key={o} value={o}>
                  {o}
                  {o === f.default ? " (default)" : ""}
                </option>
              ))}
            </select>
            <span style={{ display: "block", fontSize: 12, opacity: 0.7 }}>
              {f.description}
            </span>
          </label>
        );
      })}
      <button
        type="button"
        data-testid="save-school-flags"
        onClick={persist}
        style={{ marginTop: 8, padding: "8px 12px" }}
      >
        Save for next cast
      </button>
      {saved ? (
        <p data-testid="school-flags-saved" style={{ fontSize: 13 }}>
          Saved — new casts will include these flags.
        </p>
      ) : null}
      <pre data-testid="cast-overrides">
        {JSON.stringify(toCastOverrides(cfg), null, 2)}
      </pre>
    </form>
  );
}
