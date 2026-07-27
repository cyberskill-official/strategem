import type { MetadataRoute } from "next";

/** PWA / install metadata — brand assets under /public/brand (TASK-WEB-001). */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Tam Thức Strategem",
    short_name: "Strategem",
    description:
      "Chậm lại. Nhìn rõ. Rồi bước nhẹ. — Giáo dục di sản và chỗ dựa để suy nghĩ · Kỳ Môn · Lục Nhâm · Thái Ất",
    start_url: "/",
    display: "standalone",
    background_color: "#FDFBF6",
    theme_color: "#45210E",
    icons: [
      {
        src: "/brand/strategem-mark.svg",
        type: "image/svg+xml",
        sizes: "any",
        purpose: "any",
      },
      {
        src: "/brand/strategem-mark.png",
        type: "image/png",
        sizes: "512x512",
        purpose: "any",
      },
    ],
  };
}
