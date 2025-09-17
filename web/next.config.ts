import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "icons.brapi.dev" },
    ],
  },
};

export default nextConfig;
