/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'res.cloudinary.com',
        pathname: '**',
      },
      {
        protocol: 'https',
        hostname: 'raw.githubusercontent.com',
        pathname: '**',
      },
    ],
  },
  // When building for production, this creates a standalone folder that can be deployed without
  // the entire node_modules directory, making the final Docker image much smaller
  output: 'standalone',

  // Tymczasowo wyłącz ESLint podczas budowania
  eslint: {
    ignoreDuringBuilds: true,
  },

  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      'node:async_hooks': false, // Ignoruj moduł async_hooks
    };
    return config;
  },
};

export default nextConfig;
