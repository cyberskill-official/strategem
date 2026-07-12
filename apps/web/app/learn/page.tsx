"use client";

import Link from "next/link";
import { useLocale } from "../../src/components/i18n/locale-provider";

const PATHS = [
  { title: "learn.path1.title", body: "learn.path1.body", glyph: "主" },
  { title: "learn.path2.title", body: "learn.path2.body", glyph: "盤" },
  { title: "learn.path3.title", body: "learn.path3.body", glyph: "引" },
] as const;

export default function LearnPage() {
  const { t } = useLocale();

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
        {PATHS.map((p) => (
          <article key={p.title} className="cs-card cs-pillar">
            <div className="cs-system-tile__glyph" aria-hidden>
              {p.glyph}
            </div>
            <h2 style={{ marginTop: 12 }}>{t(p.title)}</h2>
            <p className="cs-muted">{t(p.body)}</p>
          </article>
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
