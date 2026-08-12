import type { NextConfig } from "next";

/**
 * Server-side / rewrite origin for the Python API.
 * In Docker compose this MUST be the service DNS name (http://api:8000), never
 * the host-published NEXT_PUBLIC_API_BASE (127.0.0.1:18000 is unreachable from web).
 */
const apiOrigin = (
  process.env.API_URL ||
  process.env.API_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_PROXY_TARGET ||
  "http://127.0.0.1:8000"
).replace(/\/$/, "");

const SECURITY_HEADERS: { key: string; value: string }[] = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "X-Frame-Options", value: "DENY" },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=()",
  },
  {
    key: "Content-Security-Policy-Report-Only",
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: blob:",
      "font-src 'self' data:",
      "connect-src 'self' https:",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join("; "),
  },
];

const nextConfig: NextConfig = {
  // Required for deploy/docker/web.Dockerfile multi-stage COPY of .next/standalone
  output: "standalone",
  // The DS ships raw JSX component sources (see src/ds/index.ts shim); the
  // bundler must transpile them since node_modules is skipped by default.
  transpilePackages: ["@cyberskill/design"],
  async headers() {
    return [{ source: "/:path*", headers: SECURITY_HEADERS }];
  },
  async rewrites() {
    return [
      {
        // App-router handlers under /api/auth/* take precedence over this rewrite.
        source: "/api/:path*",
        destination: `${apiOrigin}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
