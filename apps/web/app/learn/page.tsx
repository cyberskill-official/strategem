"use client";

import Link from "next/link";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { LEARN_MODULES } from "../../src/lib/learn/modules";
import type { Locale } from "../../src/i18n/routing";

export default function LearnPage() {
  const { t, locale } = useLocale();
  const loc = locale as Locale;

  return (
    <div className="cs-page cs-reveal" data-testid="learn-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("learn.kicker")}</p>
        <h1>{t("learn.title")}</h1>
        <p className="cs-lead-short">{t("learn.lead")}</p>
      </header>

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

      <section className="cs-cta-band">
        <div>
          <h2>{t("wow.nextStep")}</h2>
          <p>{t("learn.disclaimer")}</p>
        </div>
        <div className="cs-cta-actions">
          <Link
            href="/cast"
            className="cs-link-btn cs-link-btn--accent cs-link-btn--pulse"
          >
            {t("learn.ctaCast")}
          </Link>
          <Link
            href="/results/demo-ky-mon-showcase"
            className="cs-link-btn cs-link-btn--secondary"
          >
            {t("learn.ctaExplore")}
          </Link>
        </div>
      </section>
    </div>
  );
}
