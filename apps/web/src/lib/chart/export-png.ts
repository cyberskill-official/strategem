/** PNG export seam — FR-CHART-004 (browser canvas path). */

import { exportSvg } from "./export-svg";

export async function exportPng(
  root: Element,
  scale = 2,
): Promise<{ type: string; sizeHint: number; svg: string }> {
  // Headless-safe: return metadata + SVG source; browser can rasterize.
  const svg = exportSvg(root);
  return {
    type: "image/png",
    sizeHint: Math.round(svg.length * scale),
    svg,
  };
}
