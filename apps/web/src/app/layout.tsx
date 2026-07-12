import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AppShell } from "../components/app-shell/app-shell";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Tam Thức Strategem",
  description:
    "Hỗ trợ quyết định chiến lược · Kỳ Môn · Lục Nhâm · Thái Ất — Qi Men · Liu Ren · Tai Yi",
};

/** Mirror of apps/web/app/layout.tsx — Next uses app/ at package root. */
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="vi">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
