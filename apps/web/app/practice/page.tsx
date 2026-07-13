"use client";

/**
 * COV-014 — auto-graded chart practice (engine as marker, seats only).
 */

import { useState } from "react";
import Link from "next/link";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { apiBase, cast } from "../../src/lib/api/client";

type CellDiff = { kind: string; id: string; message: string };

export default function PracticePage() {
  const { t } = useLocale();
  const [system, setSystem] = useState<"qimen" | "liuren">("qimen");
  const [guess, setGuess] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [score, setScore] = useState<number | null>(null);
  const [passed, setPassed] = useState<boolean | null>(null);
  const [diffs, setDiffs] = useState<CellDiff[]>([]);
  const [feedback, setFeedback] = useState("");
  const [expected, setExpected] = useState<string[]>([]);

  async function onGrade(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setDiffs([]);
    try {
      const castRes = await cast(system, {
        datetime: "2004-01-01T10:30:00",
        tz: "+07:00",
        kinh_do: 106.7,
        place: "Ha Noi",
        question_type: "trach_thoi",
        systems: [system],
        persona_level: "beginner",
      });
      const chart = castRes.charts?.[system] || Object.values(castRes.charts || {})[0];
      const envelope = chart || {};
      const student_seat_ids = guess
        .split(/[\s,]+/)
        .map((s) => s.trim())
        .filter(Boolean);
      const res = await fetch(`${apiBase()}/api/v1/edu/practice/grade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          system,
          student_seat_ids,
          engine_envelope: envelope,
        }),
      });
      const body = await res.json();
      if (!res.ok) {
        setError(body?.error?.message || t("practice.error"));
        return;
      }
      setScore(body.score);
      setPassed(body.passed);
      setDiffs(body.cell_diffs || []);
      setFeedback(body.feedback || "");
      setExpected(body.expected_ids || []);
    } catch {
      setError(t("practice.errorNetwork"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cs-page cs-reveal" data-testid="practice-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("practice.kicker")}</p>
        <h1>{t("practice.title")}</h1>
        <p className="cs-lead-short">{t("practice.subtitle")}</p>
      </header>

      <form className="cs-card" onSubmit={onGrade} data-testid="practice-form">
        <fieldset className="cs-chip-field">
          <legend>{t("practice.system")}</legend>
          <div className="cs-chip-row">
            {(["qimen", "liuren"] as const).map((s) => (
              <button
                key={s}
                type="button"
                className={`cs-chip${system === s ? " is-active" : ""}`}
                onClick={() => setSystem(s)}
                data-testid={`practice-sys-${s}`}
              >
                {s === "qimen" ? "Kỳ Môn" : "Lục Nhâm"}
              </button>
            ))}
          </div>
        </fieldset>
        <label>
          <span className="cs-muted">{t("practice.guess")}</span>
          <input
            value={guess}
            onChange={(e) => setGuess(e.target.value)}
            placeholder="id1, id2, …"
            data-testid="practice-guess"
          />
        </label>
        <p className="cs-muted" style={{ fontSize: "0.85rem" }}>
          {t("practice.note")}
        </p>
        <button
          type="submit"
          className="cs-link-btn cs-link-btn--primary"
          disabled={loading}
          data-testid="practice-grade"
        >
          {loading ? t("practice.loading") : t("practice.submit")}
        </button>
      </form>

      {error ? (
        <p className="cs-card" role="alert">
          {error}
        </p>
      ) : null}

      {score != null ? (
        <section className="cs-card" data-testid="practice-result">
          <p>
            {t("practice.score")}: <strong>{(score * 100).toFixed(0)}%</strong>{" "}
            {passed ? "✓" : "·"}
          </p>
          <p className="cs-muted">{feedback}</p>
          {expected.length ? (
            <p className="cs-muted" style={{ fontSize: "0.85rem" }}>
              {t("practice.expected")}: {expected.join(", ")}
            </p>
          ) : null}
          {diffs.length ? (
            <ul data-testid="practice-cell-diffs">
              {diffs.map((d, i) => (
                <li key={`${d.id}-${i}`}>{d.message}</li>
              ))}
            </ul>
          ) : null}
        </section>
      ) : null}

      <p style={{ marginTop: "1rem" }}>
        <Link href="/learn">{t("practice.backLearn")}</Link>
      </p>
    </div>
  );
}
