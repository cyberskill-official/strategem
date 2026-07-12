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
      <header>
        <p className="cs-kicker">{t("learn.kicker")}</p>
        <h1>{t("learn.title")}</h1>
        <p className="cs-muted" style={{ maxWidth: "52ch" }}>
          {t("learn.lead")}
        </p>
      </header>

      <div className="cs-grid-3 cs-stagger">
        {LEARN_MODULES.map((m) => (
          <Link
            key={m.slug}
            href={`/learn/${m.slug}`}
            className="cs-card cs-pillar"
            style={{ textDecoration: "none", color: "inherit" }}
            data-learn-module={m.slug}
          >
            <div className="cs-system-tile__glyph" aria-hidden>
              {m.glyph}
            </div>
            <h2 style={{ marginTop: 12 }}>{m.title[loc] ?? m.title.vi}</h2>
            <p className="cs-muted">{m.summary[loc] ?? m.summary.vi}</p>
            <span className="cs-muted" style={{ fontWeight: 600 }}>
              {t("learn.openModule")} →
            </span>
          </Link>
        ))}
      </div>

      <section className="cs-hero-stage" style={{ marginTop: 8 }}>
        <h2>{t("wow.nextStep")}</h2>
        <p className="cs-muted" style={{ maxWidth: "48ch" }}>
          {t("learn.disclaimer")}
        </p>
        <div className="cs-hero__actions" style={{ marginTop: 16 }}>
          <Link href="/cast" className="cs-link-btn cs-link-btn--primary">
            {t("learn.ctaCast")}
          </Link>
          <Link
            href="/results/demo-ky-mon-showcase"
            className="cs-link-btn cs-link-btn--accent"
          >
            {t("learn.ctaExplore")}
          </Link>
          <Link href="/dashboard" className="cs-link-btn cs-link-btn--secondary">
            {t("nav.dashboard")}
          </Link>
        </div>
      </section>
    </div>
  );
}
