"use client";

import type { ReactNode } from "react";
import { LocaleProvider } from "../i18n/locale-provider";
import { useLocale } from "../i18n/locale-provider";
import { CounselReviewBanner } from "../domain/counsel-review-banner";
import { StickyCta } from "./sticky-cta";
import { TopBar } from "./top-bar";

function ShellFrame({ children }: { children: ReactNode }) {
  const { t } = useLocale();
  return (
    <div className="cs-shell">
      <TopBar />
      <main className="cs-main">{children}</main>
      <StickyCta />
      <footer className="cs-footer">
        <CounselReviewBanner />
        <p className="cs-disclaimer">{t("disclaimer.short")}</p>
      </footer>
    </div>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <LocaleProvider>
      <ShellFrame>{children}</ShellFrame>
    </LocaleProvider>
  );
}
