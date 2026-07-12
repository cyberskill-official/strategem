"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LocaleSwitcher } from "../i18n/locale-switcher";
import { useLocale } from "../i18n/locale-provider";

const NAV = [
  { href: "/", key: "nav.home" },
  { href: "/cast", key: "nav.cast" },
  { href: "/dashboard", key: "nav.dashboard" },
  { href: "/learn", key: "nav.learn" },
  { href: "/pricing", key: "nav.pricing" },
  { href: "/manage/history", key: "nav.history" },
  { href: "/manage/settings", key: "nav.settings" },
] as const;

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function TopBar() {
  const { t } = useLocale();
  const pathname = usePathname() ?? "/";

  return (
    <header className="cs-topbar">
      <div className="cs-topbar__inner">
        <Link href="/" className="cs-brand" data-testid="app-brand">
          <span className="cs-brand__mark" aria-hidden />
          <span className="cs-brand__text">
            <span className="cs-brand__name">{t("app.name")}</span>
            <span className="cs-brand__tagline cs-muted">{t("app.slogan")}</span>
          </span>
        </Link>

        <nav className="cs-nav" aria-label={t("app.name")}>
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="cs-nav-link"
              aria-current={isActive(pathname, item.href) ? "page" : undefined}
            >
              {t(item.key)}
            </Link>
          ))}
        </nav>

        <div className="cs-topbar__actions">
          <LocaleSwitcher />
        </div>
      </div>
    </header>
  );
}
