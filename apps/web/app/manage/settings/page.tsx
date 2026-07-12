"use client";

import { useLocale } from "../../../src/components/i18n/locale-provider";
import { SchoolFlagsForm } from "../../../src/components/manage/school-flags-form";

/** Management flow — school flags — FR-WEB-007. */
export default function ManageSettingsPage() {
  const { t } = useLocale();
  return (
    <div className="cs-page">
      <h1>{t("settings.title")}</h1>
      <div className="cs-card">
        <SchoolFlagsForm />
      </div>
    </div>
  );
}
