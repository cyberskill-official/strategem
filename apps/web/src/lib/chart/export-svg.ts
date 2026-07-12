/** SVG export seam — FR-CHART-004. */

export function exportSvg(root: Element): string {
  // Prefer an inner SVG; otherwise wrap HTML chart in foreignObject SVG.
  const svg = root.querySelector("svg");
  if (svg) {
    return new XMLSerializer().serializeToString(svg);
  }
  const w = 800;
  const h = 600;
  const html = root.outerHTML.replace(/&/g, "&amp;");
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}">
  <foreignObject width="100%" height="100%">
    <div xmlns="http://www.w3.org/1999/xhtml">${html}</div>
  </foreignObject>
</svg>`;
}
