import { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
    // TODO: Cambia esto por tu dominio real cuando lo tengas (ej: https://asistente-handling.vercel.app)
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://asistente-handling.vercel.app';

    return [
        {
            url: baseUrl,
            lastModified: new Date(),
            changeFrequency: 'yearly',
            priority: 1,
        },
        {
            url: `${baseUrl}/dashboard`,
            lastModified: new Date(),
            changeFrequency: 'monthly',
            priority: 0.8,
        },
        {
            url: `${baseUrl}/login`,
            lastModified: new Date(),
            changeFrequency: 'yearly',
            priority: 0.5,
        },
    ];
}
