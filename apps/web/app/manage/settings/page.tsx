"use client";

import { useLocale } from "../../../src/components/i18n/locale-provider";
import { SchoolFlagsForm } from "../../../src/components/manage/school-flags-form";

export default function ManageSettingsPage() {
  const { t } = useLocale();
  return (
    <div className="cs-page cs-reveal">
      <header>
        <p className="cs-kicker">{t("nav.settings")}</p>
        <h1>{t("settings.title")}</h1>
        <p className="cs-muted" style={{ maxWidth: "48ch" }}>
          {t("settings.lead")}
        </p>
      </header>
      <div className="cs-card">
        <SchoolFlagsForm />
      </div>
    </div>
  );
}
