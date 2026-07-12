"use client";

import Link from "next/link";
import { useState } from "react";
import { useLocale } from "../src/components/i18n/locale-provider";
import {
  HeroScene,
  IconCompass,
  IconDialogue,
  IconMap,
  IconQuestion,
  IconSeasons,
  IconStep,
} from "../src/components/visual/story-icons";

const STEPS = [
  { title: "home.step1.title", body: "home.step1.body", Icon: IconQuestion },
  { title: "home.step2.title", body: "home.step2.body", Icon: IconMap },
  { title: "home.step3.title", body: "home.step3.body", Icon: IconStep },
] as const;

const PAINS = [
  { title: "home.pain1.title", body: "home.pain1.body", emoji: "🔄" },
  { title: "home.pain2.title", body: "home.pain2.body", emoji: "🌿" },
  { title: "home.pain3.title", body: "home.pain3.body", emoji: "🪞" },
] as const;

const SYSTEMS = [
  {
    id: "qimen",
    plain: "system.qimen.plain",
    blurb: "system.qimen.blurb",
    name: "system.qimen",
    Icon: IconCompass,
  },
  {
    id: "liuren",
    plain: "system.liuren.plain",
    blurb: "system.liuren.blurb",
    name: "system.liuren",
    Icon: IconDialogue,
  },
  {
    id: "taiyi",
    plain: "system.taiyi.plain",
    blurb: "system.taiyi.blurb",
    name: "system.taiyi",
    Icon: IconSeasons,
  },
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
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  return (
    <div className="cs-page cs-reveal">
      <section className="cs-hero-stage cs-hero-stage--story">
        <p className="cs-kicker">{t("home.kicker")}</p>
        <h1 className="cs-hero__title vn-text">{t("home.heroTitle")}</h1>
        <p className="cs-hero__body vn-text">{t("home.heroBody")}</p>
        <div className="cs-hero-scene" aria-hidden>
          <HeroScene />
        </div>
        <div className="cs-hero__actions cs-hero__actions--primary">
          <Link
            href="/cast"
            className="cs-link-btn cs-link-btn--primary cs-link-btn--lg cs-link-btn--pulse"
            data-testid="home-cta-cast"
          >
            {t("home.ctaCast")}
          </Link>
        </div>
        <div className="cs-hero__soft-links">
          <Link href="/learn">{t("home.ctaLearn")}</Link>
          <span aria-hidden>·</span>
          <Link href="/pricing">{t("home.ctaPricing")}</Link>
        </div>
      </section>

      <section className="cs-section" data-testid="home-story-steps">
        <h2 className="cs-section-heading">{t("home.storyTitle")}</h2>
        <div className="cs-story-rail">
          {STEPS.map((s, i) => (
            <article key={s.title} className="cs-story-step">
              <div className="cs-story-step__num" aria-hidden>
                {i + 1}
              </div>
              <s.Icon className="cs-icon cs-icon--lg" />
              <h3>{t(s.title)}</h3>
              <p>{t(s.body)}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="cs-section">
        <h2 className="cs-section-heading">{t("home.painTitle")}</h2>
        <div className="cs-grid-3">
          {PAINS.map((p) => (
            <Link key={p.title} href="/cast" className="cs-visual-card">
              <span className="cs-visual-card__emoji" aria-hidden>
                {p.emoji}
              </span>
              <h3>{t(p.title)}</h3>
              <p>{t(p.body)}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className="cs-section">
        <h2 className="cs-section-heading">{t("home.systemsTitle")}</h2>
        <p className="cs-lead-short">{t("home.systemsBody")}</p>
        <div className="cs-grid-3">
          {SYSTEMS.map((s) => (
            <Link
              key={s.id}
              href={`/cast?system=${s.id}`}
              className="cs-visual-card cs-visual-card--door"
            >
              <s.Icon className="cs-icon" />
              <h3>{t(s.plain)}</h3>
              <p>{t(s.blurb)}</p>
              <span className="cs-visual-card__tag">{t(s.name)}</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="cs-diff-band" data-testid="home-diff">
        <h2 className="cs-section-heading">{t("home.diffTitle")}</h2>
        <div className="cs-diff-grid">
          <div className="cs-diff-col">
            <p className="cs-diff-label">{t("home.diff.themLabel")}</p>
            <ul>
              <li>{t("home.diff.them1")}</li>
              <li>{t("home.diff.them2")}</li>
              <li>{t("home.diff.them3")}</li>
            </ul>
          </div>
          <div className="cs-diff-col">
            <p className="cs-diff-label cs-diff-label--us">{t("home.diff.usLabel")}</p>
            <ul className="cs-diff-grid__us">
              <li>{t("home.diff.us1")}</li>
              <li>{t("home.diff.us2")}</li>
              <li>{t("home.diff.us3")}</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="cs-cta-band" data-testid="home-packages-teaser">
        <div>
          <h2>{t("home.packagesTitle")}</h2>
          <p>{t("home.packagesBody")}</p>
        </div>
        <Link href="/pricing" className="cs-link-btn cs-link-btn--accent">
          {t("nav.pricing")}
        </Link>
      </section>

      <section className="cs-section" data-testid="home-faq">
        <h2 className="cs-section-heading">{t("home.faqTitle")}</h2>
        <div className="cs-faq-list">
          {FAQS.map((f, i) => {
            const open = openFaq === i;
            return (
              <div key={f.q} className="cs-faq-item">
                <button
                  type="button"
                  aria-expanded={open}
                  onClick={() => setOpenFaq(open ? null : i)}
                >
                  {t(f.q)}
                  <span aria-hidden>{open ? "−" : "+"}</span>
                </button>
                {open ? <p>{t(f.a)}</p> : null}
              </div>
            );
          })}
        </div>
      </section>

      <p className="cs-disclaimer">{t("disclaimer.short")}</p>
    </div>
  );
}
