import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Be_Vietnam_Pro } from "next/font/google";
import { AppShell } from "../src/components/app-shell/app-shell";
// Design foundation: @cyberskill/design tokens + .cs-* classes first, then app overrides.
import "@cyberskill/design/styles.css";
import "../src/styles/globals.css";

/** Apply persisted theme before first paint (no flash of wrong theme). */
const THEME_INIT = `try{var t=localStorage.getItem("cs-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t);}catch(e){}`;

const beVietnamPro = Be_Vietnam_Pro({
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
  display: "swap",
  variable: "--font-be-vietnam-pro",
});

export const metadata: Metadata = {
  // VI-first defaults; client locale updates documentElement.lang via LocaleProvider.
  title: {
    default: "Tam Thức Strategem",
    template: "%s · Tam Thức Strategem",
  },
  description:
    "Giáo dục di sản và hỗ trợ quyết định · Kỳ Môn · Lục Nhâm · Thái Ất — heritage education & decision support",
  openGraph: {
    title: "Tam Thức Strategem",
    description:
      "Giáo dục di sản và hỗ trợ quyết định — không phải bói toán. Heritage education & decision support.",
    locale: "vi_VN",
    alternateLocale: ["en_US", "zh_CN"],
  },
  alternates: {
    languages: {
      vi: "/",
      en: "/",
      zh: "/",
    },
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="vi" className={beVietnamPro.variable} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT }} />
      </head>
      <body className={beVietnamPro.className}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
