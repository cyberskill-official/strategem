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
  title: "Tam Thức Strategem",
  description:
    "Hỗ trợ quyết định chiến lược · Kỳ Môn · Lục Nhâm · Thái Ất — Qi Men · Liu Ren · Tai Yi",
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
