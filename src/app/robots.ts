import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
    // TODO: Cambia esto por tu dominio real cuando lo tengas
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://asistentehandling.es';

    return {
        rules: {
            userAgent: '*',
            allow: '/',
            disallow: '/private/',
        },
        sitemap: `${baseUrl}/sitemap.xml`,
    };
}
