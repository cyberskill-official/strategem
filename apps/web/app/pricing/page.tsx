"use client";

import Link from "next/link";
import { useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";

const TIERS = [
  {
    id: "free",
    name: "pricing.free.name",
    price: "pricing.free.price",
    bullets: ["pricing.free.b1", "pricing.free.b2", "pricing.free.b3"],
    cta: "pricing.free.cta",
    href: "/cast",
    featured: false,
    waitlist: false,
  },
  {
    id: "insight",
    name: "pricing.insight.name",
    price: "pricing.insight.price",
    bullets: ["pricing.insight.b1", "pricing.insight.b2", "pricing.insight.b3"],
    cta: "pricing.insight.cta",
    href: "#waitlist",
    featured: true,
    waitlist: true,
  },
  {
    id: "deep",
    name: "pricing.deep.name",
    price: "pricing.deep.price",
    bullets: ["pricing.deep.b1", "pricing.deep.b2", "pricing.deep.b3"],
    cta: "pricing.deep.cta",
    href: "#waitlist",
    featured: false,
    waitlist: true,
  },
  {
    id: "advisory",
    name: "pricing.advisory.name",
    price: "pricing.advisory.price",
    bullets: ["pricing.advisory.b1", "pricing.advisory.b2", "pricing.advisory.b3"],
    cta: "pricing.advisory.cta",
    href: "#waitlist",
    featured: false,
    waitlist: true,
  },
] as const;

export default function PricingPage() {
  const { t } = useLocale();
  const [note, setNote] = useState("");
  const [ok, setOk] = useState(false);

  return (
    <div className="cs-page cs-reveal" data-testid="pricing-page">
      <header>
        <p className="cs-kicker">{t("pricing.kicker")}</p>
        <h1>{t("pricing.title")}</h1>
        <p className="cs-muted" style={{ maxWidth: "48ch" }}>
          {t("pricing.lead")}
        </p>
      </header>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 16,
        }}
      >
        {TIERS.map((tier) => (
          <article
            key={tier.id}
            className={`cs-card${tier.featured ? " cs-card--raised" : ""}`}
            data-tier={tier.id}
            style={
              tier.featured
                ? { borderColor: "var(--cs-color-brand-ochre)", boxShadow: "var(--cs-shadow-md)" }
                : undefined
            }
          >
            <h2 style={{ fontSize: "1.15rem" }}>{t(tier.name)}</h2>
            <p
              style={{
                fontSize: "1.5rem",
                fontWeight: 700,
                color: "var(--cs-color-brand-umber)",
                margin: "8px 0 16px",
              }}
            >
              {t(tier.price)}
            </p>
            <ul className="cs-muted" style={{ paddingLeft: 18, lineHeight: 1.65, minHeight: 100 }}>
              {tier.bullets.map((b) => (
                <li key={b}>{t(b)}</li>
              ))}
            </ul>
            {tier.waitlist ? (
              <a href="#waitlist" className="cs-link-btn cs-link-btn--secondary" style={{ width: "100%" }}>
                {t(tier.cta)}
              </a>
            ) : (
              <Link
                href={tier.href}
                className="cs-link-btn cs-link-btn--primary"
                style={{ width: "100%" }}
              >
                {t(tier.cta)}
              </Link>
            )}
          </article>
        ))}
      </div>

      <p className="cs-disclaimer">{t("pricing.note")}</p>

      <section id="waitlist" className="cs-card" style={{ maxWidth: 520 }}>
        <h2>{t("pricing.insight.cta")}</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            try {
              const key = "tamthuc.waitlist.v1";
              const prev = JSON.parse(localStorage.getItem(key) || "[]") as string[];
              if (note.trim()) {
                prev.push(note.trim());
                localStorage.setItem(key, JSON.stringify(prev.slice(-50)));
              }
              setOk(true);
              setNote("");
            } catch {
              setOk(true);
            }
          }}
          style={{ display: "grid", gap: 12 }}
        >
          <label>
            {t("pricing.advisory.cta")}
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
              placeholder="…"
              data-testid="waitlist-note"
            />
          </label>
          <button type="submit" className="cs-link-btn cs-link-btn--primary" style={{ border: "none" }}>
            {t("pricing.insight.cta")}
          </button>
          {ok ? (
            <p className="cs-muted" data-testid="waitlist-ok">
              {t("pricing.waitlistOk")}
            </p>
          ) : null}
        </form>
      </section>
    </div>
  );
}
