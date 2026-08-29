"use client";

import Link from "next/link";
import { useLocale } from "../i18n/locale-provider";

const FLOWS = [
  {
    id: "lookup",
    titleKey: "dashboard.flow.lookup",
    descKey: "dashboard.flow.lookupDesc",
    href: "/cast",
  },
  {
    id: "timing",
    titleKey: "dashboard.flow.timing",
    descKey: "dashboard.flow.timingDesc",
    href: "/timing",
  },
  {
    id: "learning",
    titleKey: "dashboard.flow.learning",
    descKey: "dashboard.flow.learningDesc",
    href: "/learn",
  },
  {
    id: "management",
    titleKey: "dashboard.flow.management",
    descKey: "dashboard.flow.managementDesc",
    href: "/manage/history",
  },
] as const;

export function FlowEntryCards() {
  const { t } = useLocale();
  return (
    <section data-testid="flow-entry-cards" className="cs-section">
      <h2 className="cs-section-heading">{t("dashboard.flows")}</h2>
      <div className="cs-grid-3">
        {FLOWS.map((f) => (
          <Link key={f.id} href={f.href} data-flow={f.id} className="cs-flow-card">
            <span className="cs-flow-card__title">{t(f.titleKey)}</span>
            <span className="cs-muted">{t(f.descKey)}</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
