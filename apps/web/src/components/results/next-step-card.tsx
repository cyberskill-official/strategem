"use client";

import Link from "next/link";
import { useState } from "react";
import { useLocale } from "../i18n/locale-provider";

export function NextStepCard({
  systemLabel,
  patternHint,
}: {
  systemLabel?: string;
  patternHint?: string;
}) {
  const { t } = useLocale();
  const [copied, setCopied] = useState(false);

  const teaser = [
    t("app.name"),
    systemLabel ? `· ${systemLabel}` : "",
    patternHint ? `· ${patternHint}` : "",
    "—",
    t("results.nextBody"),
  ]
    .filter(Boolean)
    .join(" ");

  async function share() {
    try {
      if (navigator.share) {
        await navigator.share({ text: teaser, title: t("app.name") });
        return;
      }
    } catch {
      /* fall through */
    }
    try {
      await navigator.clipboard.writeText(teaser);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <aside className="cs-upsell" data-testid="results-next-step">
      <h2 style={{ margin: 0 }}>{t("results.nextTitle")}</h2>
      <p className="cs-muted" style={{ margin: 0 }}>
        {t("results.nextBody")}
      </p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
        <Link href="/pricing" className="cs-link-btn cs-link-btn--accent">
          {t("results.upsellPricing")}
        </Link>
        <Link href="/learn/cach-cuc" className="cs-link-btn cs-link-btn--secondary">
          {t("results.upsellLearn")}
        </Link>
        <button
          type="button"
          className="cs-link-btn cs-link-btn--primary"
          style={{ border: "none", cursor: "pointer" }}
          data-testid="share-insight"
          onClick={() => void share()}
        >
          {copied ? t("results.shareCopied") : t("results.shareInsight")}
        </button>
      </div>
    </aside>
  );
}
