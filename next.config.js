/** @type {import('next').NextConfig} */
const nextConfig = {
    // output: 'export', // Comentado para Railway (SSR)
    // trailingSlash: true, // No necesario en SSR
    images: {
        unoptimized: true,
    },
};

module.exports = nextConfig;
