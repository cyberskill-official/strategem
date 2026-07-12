"use client";

import Link from "next/link";
import { useState } from "react";
import { useLocale } from "../src/components/i18n/locale-provider";

const SYSTEMS = [
  { id: "qimen", key: "system.qimen", blurb: "system.qimen.blurb", glyph: "奇" },
  { id: "liuren", key: "system.liuren", blurb: "system.liuren.blurb", glyph: "壬" },
  { id: "taiyi", key: "system.taiyi", blurb: "system.taiyi.blurb", glyph: "乙" },
] as const;

const PAINS = [
  { title: "home.pain1.title", body: "home.pain1.body" },
  { title: "home.pain2.title", body: "home.pain2.body" },
  { title: "home.pain3.title", body: "home.pain3.body" },
] as const;

const FAQS = [
  { q: "home.faq1.q", a: "home.faq1.a" },
  { q: "home.faq2.q", a: "home.faq2.a" },
  { q: "home.faq3.q", a: "home.faq3.a" },
  { q: "home.faq4.q", a: "home.faq4.a" },
  { q: "home.faq5.q", a: "home.faq5.a" },
] as const;

export default function HomePage() {
  const { t } = useLocale();
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  return (
    <div className="cs-page cs-reveal">
      <section className="cs-hero-stage">
        <p className="cs-kicker">{t("home.kicker")}</p>
        <h1 className="cs-hero__title vn-text">{t("home.heroTitle")}</h1>
        <p className="cs-hero__body vn-text" style={{ maxWidth: "48ch", fontSize: "1.1rem" }}>
          {t("home.heroBody")}
        </p>
        <div className="cs-hero__actions" style={{ marginTop: 24 }}>
          <Link href="/cast" className="cs-link-btn cs-link-btn--primary" data-testid="home-cta-cast">
            {t("home.ctaCast")}
          </Link>
          <Link href="/pricing" className="cs-link-btn cs-link-btn--accent" data-testid="home-cta-pricing">
            {t("home.ctaPricing")}
          </Link>
          <Link href="/learn" className="cs-link-btn cs-link-btn--secondary">
            {t("home.ctaLearn")}
          </Link>
        </div>
        <div className="cs-stat-row">
          <div className="cs-stat">
            <div className="cs-stat__value">3</div>
            <div className="cs-stat__label">{t("home.statBoards")}</div>
          </div>
          <div className="cs-stat">
            <div className="cs-stat__value">0₫</div>
            <div className="cs-stat__label">{t("pricing.free.price")}</div>
          </div>
          <div className="cs-stat">
            <div className="cs-stat__value">1:1</div>
            <div className="cs-stat__label">{t("home.statCitations")}</div>
          </div>
        </div>
      </section>

      <section>
        <h2>{t("home.painTitle")}</h2>
        <div className="cs-grid-3 cs-stagger">
          {PAINS.map((p) => (
            <article key={p.title} className="cs-card cs-pillar">
              <h3>{t(p.title)}</h3>
              <p className="cs-muted">{t(p.body)}</p>
              <Link href="/cast" className="cs-muted" style={{ fontWeight: 600 }}>
                {t("home.ctaCast")} →
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="cs-card" data-testid="home-diff">
        <h2>{t("home.diffTitle")}</h2>
        <div className="cs-grid-2" style={{ marginTop: 16 }}>
          <ul className="cs-muted" style={{ lineHeight: 1.7 }}>
            <li>{t("home.diff.them1")}</li>
            <li>{t("home.diff.them2")}</li>
            <li>{t("home.diff.them3")}</li>
          </ul>
          <div style={{ borderLeft: "3px solid var(--cs-color-brand-ochre)", paddingLeft: 16 }}>
            <ul style={{ lineHeight: 1.7, fontWeight: 550 }}>
              <li>{t("home.diff.us1")}</li>
              <li>{t("home.diff.us2")}</li>
              <li>{t("home.diff.us3")}</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="cs-card cs-card--raised" data-testid="home-packages-teaser">
        <h2>{t("home.packagesTitle")}</h2>
        <p className="cs-muted" style={{ maxWidth: "52ch" }}>
          {t("home.packagesBody")}
        </p>
        <Link href="/pricing" className="cs-link-btn cs-link-btn--primary" style={{ marginTop: 8 }}>
          {t("nav.pricing")} →
        </Link>
      </section>

      <section>
        <h2>{t("home.systemsTitle")}</h2>
        <p className="cs-muted">{t("home.systemsBody")}</p>
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

      <section className="cs-card">
        <h2>{t("home.proofTitle")}</h2>
        <p className="cs-muted" data-testid="home-proof-empty">
          {t("home.proofEmpty")}
        </p>
      </section>

      <section data-testid="home-faq">
        <h2>{t("home.faqTitle")}</h2>
        <div style={{ display: "grid", gap: 8 }}>
          {FAQS.map((f, i) => {
            const open = openFaq === i;
            return (
              <div key={f.q} className="cs-card" style={{ padding: 0, overflow: "hidden" }}>
                <button
                  type="button"
                  onClick={() => setOpenFaq(open ? null : i)}
                  aria-expanded={open}
                  style={{
                    width: "100%",
                    textAlign: "left",
                    padding: "14px 18px",
                    border: "none",
                    background: "transparent",
                    font: "inherit",
                    fontWeight: 650,
                    cursor: "pointer",
                    color: "var(--cs-color-brand-umber)",
                  }}
                >
                  {t(f.q)}
                </button>
                {open ? (
                  <p className="cs-muted" style={{ padding: "0 18px 16px", margin: 0 }}>
                    {t(f.a)}
                  </p>
                ) : null}
              </div>
            );
          })}
        </div>
      </section>

      <p className="cs-disclaimer">{t("disclaimer.short")}</p>
    </div>
  );
}
