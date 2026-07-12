"use client";

import Link from "next/link";
import { useLocale } from "../src/components/i18n/locale-provider";

export default function HomePage() {
  const { t } = useLocale();

  return (
    <div className="cs-page">
      <section className="cs-hero">
        <h1 className="cs-hero__title vn-text">{t("home.heroTitle")}</h1>
        <p className="cs-hero__body vn-text">{t("home.heroBody")}</p>
        <div className="cs-hero__actions">
          <Link href="/cast" className="cs-link-btn cs-link-btn--primary">
            {t("home.ctaCast")}
          </Link>
          <Link href="/dashboard" className="cs-link-btn cs-link-btn--secondary">
            {t("home.ctaDashboard")}
          </Link>
        </div>
      </section>

      <section className="cs-pillars" aria-label={t("app.tagline")}>
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
    </div>
  );
}
