import { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
    return {
        name: 'Asistente Handling',
        short_name: 'Asistente',
        description: 'Tu asistente legal y laboral para el sector de Handling',
        start_url: '/dashboard',
        display: 'standalone',
        background_color: '#0f172a',
        theme_color: '#0f172a',
        icons: [
            {
                src: '/logoapp.png',
                sizes: '512x512', // Assuming user wants this used as the main icon
                type: 'image/png',
                purpose: 'any',
            },
            {
                src: '/logoapp.png',
                sizes: '512x512',
                type: 'image/png',
                purpose: 'maskable',
            },
        ],
    };
}
