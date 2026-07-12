import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Be_Vietnam_Pro } from "next/font/google";
import { AppShell } from "../src/components/app-shell/app-shell";
import "../src/styles/globals.css";

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
    <html lang="vi" className={beVietnamPro.variable}>
      <body className={beVietnamPro.className}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
