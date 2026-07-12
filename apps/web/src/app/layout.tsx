import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AppShell } from "../components/app-shell/app-shell";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Tam Thuc Strategem",
  description: "QiMen · LiuRen · TaiYi strategic decision support",
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
