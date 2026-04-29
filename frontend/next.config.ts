import type { NextConfig } from "next";

const isProd = process.env.NEXT_PUBLIC_ENVIRONMENT === "production";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: isProd ? "export" : undefined,
  basePath: isProd ? "/lesson-plan-generator" : "",
  assetPrefix: isProd ? "/lesson-plan-generator/" : "",
  images: {
    unoptimized: isProd,
  },
};

export default nextConfig;