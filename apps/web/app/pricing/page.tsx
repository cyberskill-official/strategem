"use client";

import Link from "next/link";
import { useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { apiBase } from "../../src/lib/api/client";

/**
 * COV-026: free cast open; single Stripe rail for premium; advisory stays waitlist.
 */
const TIERS = [
  {
    id: "free",
    name: "pricing.free.name",
    price: "pricing.free.price",
    bullets: ["pricing.free.b1", "pricing.free.b2", "pricing.free.b3"],
    cta: "pricing.free.cta",
    href: "/cast",
    featured: true,
    mode: "free" as const,
    emoji: "🗺️",
  },
  {
    id: "premium",
    name: "pricing.insight.name",
    price: "pricing.insight.price",
    bullets: ["pricing.insight.b1", "pricing.insight.b2", "pricing.insight.b3"],
    cta: "pricing.premium.cta",
    href: "#checkout",
    featured: false,
    mode: "checkout" as const,
    emoji: "🔍",
  },
  {
    id: "advisory",
    name: "pricing.advisory.name",
    price: "pricing.advisory.price",
    bullets: ["pricing.advisory.b1", "pricing.advisory.b2", "pricing.advisory.b3"],
    cta: "pricing.advisory.cta",
    href: "#waitlist",
    featured: false,
    mode: "waitlist" as const,
    emoji: "🤝",
  },
] as const;

export default function PricingPage() {
  const { t } = useLocale();
  const [note, setNote] = useState("");
  const [ok, setOk] = useState(false);
  const [checkoutMsg, setCheckoutMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function startCheckout() {
    setLoading(true);
    setCheckoutMsg(null);
    try {
      const res = await fetch(`${apiBase()}/api/v1/payments/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "local-user",
          success_url: typeof window !== "undefined" ? `${window.location.origin}/pricing?paid=1` : "/pricing",
          cancel_url: typeof window !== "undefined" ? `${window.location.origin}/pricing?cancelled=1` : "/pricing",
        }),
      });
      const body = await res.json();
      if (!res.ok) {
        setCheckoutMsg(body?.error?.message || t("pricing.checkoutError"));
        return;
      }
      const url = body.checkout_url as string;
      setCheckoutMsg(
        body.mode === "mock_contract"
          ? t("pricing.checkoutMock")
          : t("pricing.checkoutRedirect"),
      );
      if (url && body.mode === "live" && typeof window !== "undefined") {
        window.location.href = url;
      }
    } catch {
      setCheckoutMsg(t("pricing.checkoutError"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cs-page cs-reveal" data-testid="pricing-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("pricing.kicker")}</p>
        <h1>{t("pricing.title")}</h1>
        <p className="cs-lead-short">{t("pricing.lead")}</p>
      </header>

      <p className="cs-disclaimer" data-testid="single-rail-note">
        {t("pricing.singleRail")}
      </p>

      <div className="cs-pricing-grid">
        {TIERS.map((tier) => (
          <article
            key={tier.id}
            className={`cs-visual-card${tier.featured ? " is-active" : ""}`}
            data-tier={tier.id}
          >
            <span className="cs-visual-card__emoji" aria-hidden>
              {tier.emoji}
            </span>
            <h2>{t(tier.name)}</h2>
            <p className="cs-price">{t(tier.price)}</p>
            <ul>
              {tier.bullets.map((b) => (
                <li key={b}>{t(b)}</li>
              ))}
            </ul>
            {tier.mode === "checkout" ? (
              <button
                type="button"
                className="cs-link-btn cs-link-btn--primary"
                onClick={() => void startCheckout()}
                disabled={loading}
                data-testid="premium-checkout"
              >
                {loading ? t("pricing.checkoutLoading") : t(tier.cta)}
              </button>
            ) : tier.mode === "waitlist" ? (
              <a href="#waitlist" className="cs-link-btn cs-link-btn--secondary">
                {t(tier.cta)}
              </a>
            ) : (
              <Link href={tier.href} className="cs-link-btn cs-link-btn--primary">
                {t(tier.cta)}
              </Link>
            )}
          </article>
        ))}
      </div>

      {checkoutMsg ? (
        <p className="cs-card" data-testid="checkout-msg">
          {checkoutMsg}
        </p>
      ) : null}

      <p className="cs-disclaimer">{t("pricing.note")}</p>
      <p className="cs-disclaimer" data-testid="waitlist-local-note">
        {t("pricing.waitlistLocal")}
      </p>

      <section id="waitlist" className="cs-card cs-waitlist-card">
        <h2 className="cs-subhead" style={{ marginTop: 0 }}>
          {t("pricing.advisory.cta")}
        </h2>
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
          className="cs-query-form"
        >
          <label>
            {t("pricing.advisory.cta")}
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={2}
              data-testid="waitlist-note"
            />
          </label>
          <button type="submit" className="cs-link-btn cs-link-btn--primary" style={{ border: "none" }}>
            {t("pricing.insight.cta")}
          </button>
          {ok ? (
            <p className="cs-muted" data-testid="waitlist-ok" style={{ margin: 0 }}>
              {t("pricing.waitlistOk")}
            </p>
          ) : null}
        </form>
      </section>
    </div>
  );
}
