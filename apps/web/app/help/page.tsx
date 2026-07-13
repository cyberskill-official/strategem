"use client";

/** COV-016 — help center + re-openable onboarding. */

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { apiBase } from "../../src/lib/api/client";

const ONBOARD_KEY = "tamthuc.onboarding.done.v1";

type Step = { id: string; title: string; body: string; cta?: string; href?: string };
type Help = { id: string; title: string; body: string; tags?: string[] };

export default function HelpPage() {
  const { t } = useLocale();
  const [steps, setSteps] = useState<Step[]>([]);
  const [help, setHelp] = useState<Help[]>([]);
  const [q, setQ] = useState("");
  const [stepIdx, setStepIdx] = useState(0);
  const [showOnboard, setShowOnboard] = useState(() => {
    if (typeof window === "undefined") return false;
    try {
      return localStorage.getItem(ONBOARD_KEY) !== "1";
    } catch {
      return true;
    }
  });

  useEffect(() => {
    let cancelled = false;
    // Defer so setState is not synchronous in the effect body (react-hooks/set-state-in-effect)
    const timer = window.setTimeout(() => {
      void (async () => {
        try {
          const res = await fetch(`${apiBase()}/api/v1/edu/onboarding`);
          const body = await res.json();
          if (cancelled) return;
          setSteps(body.steps || []);
          setHelp(body.help || []);
        } catch {
          /* soft */
        }
      })();
    }, 0);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, []);

  const filtered = useMemo(() => {
    const ql = q.trim().toLowerCase();
    if (!ql) return help;
    return help.filter(
      (h) =>
        h.title.toLowerCase().includes(ql) ||
        h.body.toLowerCase().includes(ql) ||
        (h.tags || []).some((tag) => tag.includes(ql)),
    );
  }, [help, q]);

  function finishOnboard() {
    try {
      localStorage.setItem(ONBOARD_KEY, "1");
    } catch {
      /* ignore */
    }
    setShowOnboard(false);
  }

  function reopenOnboard() {
    setStepIdx(0);
    setShowOnboard(true);
  }

  const step = steps[stepIdx];

  return (
    <div className="cs-page cs-reveal" data-testid="help-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("help.kicker")}</p>
        <h1>{t("help.title")}</h1>
        <p className="cs-lead-short">{t("help.subtitle")}</p>
      </header>

      {showOnboard && step ? (
        <section className="cs-card" data-testid="onboarding-panel">
          <p className="cs-kicker">
            {stepIdx + 1}/{steps.length}
          </p>
          <h2>{step.title}</h2>
          <p>{step.body}</p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {stepIdx < steps.length - 1 ? (
              <button
                type="button"
                className="cs-link-btn cs-link-btn--primary"
                onClick={() => setStepIdx((i) => i + 1)}
                data-testid="onboard-next"
              >
                {step.cta || t("help.next")}
              </button>
            ) : (
              <button
                type="button"
                className="cs-link-btn cs-link-btn--primary"
                onClick={finishOnboard}
                data-testid="onboard-done"
              >
                {step.cta || t("help.done")}
              </button>
            )}
            <button
              type="button"
              className="cs-link-btn cs-link-btn--secondary"
              onClick={finishOnboard}
              data-testid="onboard-skip"
            >
              {t("help.skip")}
            </button>
            {step.href ? (
              <Link href={step.href} className="cs-link-btn cs-link-btn--secondary">
                {t("help.openLink")}
              </Link>
            ) : null}
          </div>
        </section>
      ) : (
        <p>
          <button
            type="button"
            className="cs-link-btn cs-link-btn--secondary"
            onClick={reopenOnboard}
            data-testid="onboard-reopen"
          >
            {t("help.reopen")}
          </button>
        </p>
      )}

      <section className="cs-card" style={{ marginTop: "1.5rem" }} data-testid="help-catalog">
        <h2>{t("help.catalog")}</h2>
        <label>
          <span className="cs-muted">{t("help.search")}</span>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            data-testid="help-search"
          />
        </label>
        <ul style={{ listStyle: "none", padding: 0, marginTop: "1rem" }}>
          {filtered.map((h) => (
            <li key={h.id} className="cs-card" data-testid="help-article" style={{ marginBottom: 8 }}>
              <h3 style={{ marginTop: 0 }}>{h.title}</h3>
              <p>{h.body}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
