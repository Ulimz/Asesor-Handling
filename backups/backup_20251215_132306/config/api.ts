const getApiUrl = () => {
    if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;

    // Fallback inteligente:
    // Si estamos en producción (basado en NODE_ENV), usar la URL real de Railway.
    // Si estamos en local, usar localhost.
    if (process.env.NODE_ENV === 'production') {
        return 'https://intelligent-vitality-production.up.railway.app';
    }

    return 'http://127.0.0.1:8000';
};

export const API_URL = getApiUrl();
