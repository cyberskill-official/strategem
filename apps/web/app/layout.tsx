import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AppShell } from "../src/components/app-shell/app-shell";
import "../src/styles/globals.css";

export const metadata: Metadata = {
  title: "Tam Thức Strategem",
  description:
    "Hỗ trợ quyết định chiến lược · Kỳ Môn · Lục Nhâm · Thái Ất — Qi Men · Liu Ren · Tai Yi",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="vi">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
