import type { NextConfig } from "next";

const apiOrigin =
  process.env.API_URL ||
  process.env.NEXT_PUBLIC_API_PROXY_TARGET ||
  "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Required for deploy/docker/web.Dockerfile multi-stage COPY of .next/standalone
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiOrigin.replace(/\/$/, "")}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
