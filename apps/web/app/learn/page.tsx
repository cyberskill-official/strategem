"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
import {
  CURRICULUM_LEVELS,
  isLevelUnlocked,
  loadCompletedCriteria,
  loadLearnerLevel,
  saveCompletedCriteria,
  saveLearnerLevel,
  type CurriculumLevel,
} from "../../src/lib/learn/curriculum";
import { LEARN_MODULES } from "../../src/lib/learn/modules";
import type { Locale } from "../../src/i18n/routing";

export default function LearnPage() {
  const { t, locale } = useLocale();
  const loc = locale as Locale;
  // Lazy init from localStorage (WEB-013 curriculum) — avoid setState-in-effect
  const [completed, setCompleted] = useState<Set<string>>(() => {
    if (typeof window === "undefined") return new Set();
    return loadCompletedCriteria();
  });
  const [activeLevel, setActiveLevel] = useState(() => {
    if (typeof window === "undefined") return "L1";
    return loadLearnerLevel();
  });
  const [hydrated] = useState(() => typeof window !== "undefined");

  const levels = useMemo(() => CURRICULUM_LEVELS, []);

  function toggleCriterion(id: string) {
    setCompleted((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      saveCompletedCriteria(next);
      return next;
    });
  }

  function selectLevel(lv: CurriculumLevel) {
    if (!isLevelUnlocked(completed, lv)) return;
    setActiveLevel(lv.id);
    saveLearnerLevel(lv.id);
  }

  return (
    <div className="cs-page cs-reveal" data-testid="learn-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("learn.kicker")}</p>
        <h1>{t("learn.title")}</h1>
        <p className="cs-lead-short">{t("learn.lead")}</p>
      </header>

      {/* COV-013: L1–L4 progression */}
      <section data-testid="curriculum-levels" aria-label={t("learn.curriculumTitle")}>
        <h2 className="cs-section-heading">{t("learn.curriculumTitle")}</h2>
        <p className="cs-muted">{t("learn.curriculumLead")}</p>
        {hydrated ? (
          <p className="cs-muted" data-testid="learner-level">
            {t("learn.currentLevel")}: <strong>{activeLevel}</strong>
          </p>
        ) : null}
        <div className="cs-grid-2" style={{ gap: "1rem", marginTop: "1rem" }}>
          {levels.map((lv) => {
            const unlocked = isLevelUnlocked(completed, lv);
            const doneCount = lv.criteria.filter((c) => completed.has(c.id)).length;
            const active = activeLevel === lv.id;
            return (
              <article
                key={lv.id}
                className="cs-card"
                data-testid={`curriculum-${lv.id}`}
                data-unlocked={unlocked ? "1" : "0"}
                style={{
                  opacity: unlocked ? 1 : 0.55,
                  outline: active ? "2px solid var(--color-ochre, #c4a35a)" : undefined,
                }}
              >
                <header style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                  <div>
                    <p className="cs-kicker" style={{ margin: 0 }}>
                      {lv.id}
                    </p>
                    <h3 style={{ margin: "0.25rem 0" }}>{lv.name[loc] ?? lv.name.vi}</h3>
                  </div>
                  <button
                    type="button"
                    className="cs-link-btn cs-link-btn--secondary"
                    disabled={!unlocked}
                    onClick={() => selectLevel(lv)}
                    data-testid={`select-${lv.id}`}
                  >
                    {unlocked ? t("learn.setLevel") : t("learn.locked")}
                  </button>
                </header>
                <p className="cs-muted">{lv.summary[loc] ?? lv.summary.vi}</p>
                {lv.prerequisite ? (
                  <p className="cs-muted" style={{ fontSize: "0.85rem" }}>
                    {t("learn.prerequisite")}: {lv.prerequisite}
                  </p>
                ) : null}
                <ul style={{ listStyle: "none", padding: 0, margin: "0.75rem 0" }}>
                  {lv.criteria.map((c) => (
                    <li key={c.id} style={{ marginBottom: 6 }}>
                      <label style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                        <input
                          type="checkbox"
                          checked={completed.has(c.id)}
                          disabled={!unlocked}
                          onChange={() => toggleCriterion(c.id)}
                          data-testid={`crit-${c.id}`}
                        />
                        <span>{c.label[loc] ?? c.label.vi}</span>
                      </label>
                    </li>
                  ))}
                </ul>
                <p className="cs-muted" style={{ fontSize: "0.85rem" }}>
                  {doneCount}/{lv.criteria.length} · unlocks: {lv.unlocks.join(", ")}
                </p>
                <Link
                  href={lv.practiceHref}
                  className="cs-link-btn cs-link-btn--primary"
                  data-testid={`practice-${lv.id}`}
                  style={{ display: "inline-block", marginTop: 8 }}
                >
                  {t("learn.practice")} →
                </Link>
              </article>
            );
          })}
        </div>
      </section>

      <section style={{ marginTop: "2rem" }}>
        <h2 className="cs-section-heading">{t("learn.storiesTitle")}</h2>
        <div className="cs-grid-3 cs-stagger">
          {LEARN_MODULES.map((m, i) => (
            <Link
              key={m.slug}
              href={`/learn/${m.slug}`}
              className="cs-visual-card"
              data-learn-module={m.slug}
            >
              <span className="cs-story-step__num" aria-hidden>
                {i + 1}
              </span>
              <span className="cs-visual-card__emoji" aria-hidden>
                {m.glyph}
              </span>
              <h2>{m.title[loc] ?? m.title.vi}</h2>
              <p>{m.summary[loc] ?? m.summary.vi}</p>
              <span className="cs-visual-card__tag">{t("learn.openModule")} →</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="cs-cta-band">
        <div>
          <h2>{t("wow.nextStep")}</h2>
          <p>{t("learn.disclaimer")}</p>
        </div>
        <div className="cs-cta-actions">
          <Link
            href="/cast?system=qimen"
            className="cs-link-btn cs-link-btn--accent cs-link-btn--pulse"
          >
            {t("learn.ctaCastQimen")}
          </Link>
          <Link href="/cast?system=liuren" className="cs-link-btn cs-link-btn--secondary">
            {t("learn.ctaCastLiuren")}
          </Link>
          <Link href="/cast?system=taiyi" className="cs-link-btn cs-link-btn--secondary">
            {t("learn.ctaCastTaiyi")}
          </Link>
          <Link href="/cross-system" className="cs-link-btn cs-link-btn--secondary">
            {t("learn.ctaCross")}
          </Link>
        </div>
      </section>
    </div>
  );
}
