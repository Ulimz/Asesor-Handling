/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone', // Necesario para Dockerfile.prod
    // trailingSlash: true, // No necesario en SSR
    images: {
        unoptimized: true,
    },
};

module.exports = nextConfig;
