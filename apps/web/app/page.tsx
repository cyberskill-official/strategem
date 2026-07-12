"use client";

import Link from "next/link";
import { useLocale } from "../src/components/i18n/locale-provider";

const SYSTEMS = [
  { id: "qimen", key: "system.qimen", blurb: "system.qimen.blurb", glyph: "奇" },
  { id: "liuren", key: "system.liuren", blurb: "system.liuren.blurb", glyph: "壬" },
  { id: "taiyi", key: "system.taiyi", blurb: "system.taiyi.blurb", glyph: "乙" },
] as const;

export default function HomePage() {
  const { t } = useLocale();

  return (
    <div className="cs-page cs-reveal">
      <section className="cs-hero-stage">
        <p className="cs-kicker">{t("home.kicker")}</p>
        <h1 className="cs-hero__title vn-text">{t("home.heroTitle")}</h1>
        <p className="cs-hero__body vn-text" style={{ maxWidth: "48ch", fontSize: "1.1rem" }}>
          {t("home.heroBody")}
        </p>
        <div className="cs-hero__actions" style={{ marginTop: 24 }}>
          <Link href="/cast" className="cs-link-btn cs-link-btn--primary">
            {t("home.ctaCast")}
          </Link>
          <Link href="/dashboard" className="cs-link-btn cs-link-btn--secondary">
            {t("home.ctaDashboard")}
          </Link>
          <Link href="/cast#systems" className="cs-link-btn cs-link-btn--accent">
            {t("home.ctaExplore")}
          </Link>
        </div>
        <div className="cs-stat-row">
          <div className="cs-stat">
            <div className="cs-stat__value">3</div>
            <div className="cs-stat__label">{t("home.statBoards")}</div>
          </div>
          <div className="cs-stat">
            <div className="cs-stat__value">∞</div>
            <div className="cs-stat__label">{t("home.statPatterns")}</div>
          </div>
          <div className="cs-stat">
            <div className="cs-stat__value">1:1</div>
            <div className="cs-stat__label">{t("home.statCitations")}</div>
          </div>
        </div>
      </section>

      <section className="cs-pillars cs-stagger" aria-label={t("app.tagline")}>
        <article className="cs-card cs-pillar">
          <h2>{t("home.pillarCalc")}</h2>
          <p className="cs-muted">{t("home.pillarCalcDesc")}</p>
        </article>
        <article className="cs-card cs-pillar">
          <h2>{t("home.pillarAi")}</h2>
          <p className="cs-muted">{t("home.pillarAiDesc")}</p>
        </article>
        <article className="cs-card cs-pillar">
          <h2>{t("home.pillarDecide")}</h2>
          <p className="cs-muted">{t("home.pillarDecideDesc")}</p>
        </article>
      </section>

      <section className="cs-card">
        <div className="cs-section-title" style={{ marginBottom: 16 }}>
          <h2>{t("home.systemsTitle")}</h2>
        </div>
        <p className="cs-muted" style={{ maxWidth: "52ch" }}>
          {t("home.systemsBody")}
        </p>
        <div className="cs-grid-3" style={{ marginTop: 16 }}>
          {SYSTEMS.map((s) => (
            <Link
              key={s.id}
              href={`/cast?system=${s.id}`}
              className="cs-system-tile"
              style={{ textDecoration: "none" }}
            >
              <div className="cs-system-tile__glyph" aria-hidden>
                {s.glyph}
              </div>
              <div style={{ fontWeight: 700, fontSize: "1.1rem" }}>{t(s.key)}</div>
              <div className="cs-muted" style={{ marginTop: 4 }}>
                {t(s.blurb)}
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section className="cs-card cs-card--raised">
        <h2>{t("home.curiosityTitle")}</h2>
        <p className="cs-muted" style={{ maxWidth: "54ch", marginBottom: 16 }}>
          {t("home.curiosityBody")}
        </p>
        <Link href="/cast" className="cs-link-btn cs-link-btn--primary">
          {t("wow.nextStep")} → {t("nav.cast")}
        </Link>
      </section>
    </div>
  );
}
