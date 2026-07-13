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

const nextConfig: NextConfig = {
  // Required for deploy/docker/web.Dockerfile multi-stage COPY of .next/standalone
  output: "standalone",
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
