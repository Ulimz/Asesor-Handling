/** @type {import('next').NextConfig} */
const nextConfig = {
    trailingSlash: true,
    async rewrites() {
        const apiUrl = process.env.API_URL || "http://127.0.0.1:8000";
        console.log("[Next.js Config CJS] Rewriting routes to:", apiUrl);
        return [
            {
                source: "/api/:path*",
                destination: `${apiUrl}/:path*`,
            },
        ];
    },
};

module.exports = nextConfig;
