import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for deploy/docker/web.Dockerfile multi-stage COPY of .next/standalone
  output: "standalone",
};

export default nextConfig;
