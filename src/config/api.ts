const getApiUrl = () => {
    if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;

    // Si estamos en producción (build) y no hay variable, advertimos.
    if (process.env.NODE_ENV === 'production' && typeof window !== 'undefined') {
        console.warn('⚠️ ADVERTENCIA CRÍTICA: NEXT_PUBLIC_API_URL no está definida. La app intentará conectarse a localhost, lo cual fallará en dispositivos remotos.');
    }

    return 'http://127.0.0.1:8000';
};

export const API_URL = getApiUrl();
