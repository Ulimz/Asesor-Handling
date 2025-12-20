const getApiUrl = () => {
    // FORCE PRODUCTION URL FOR DEBUGGING
    return 'https://intelligent-vitality-production.up.railway.app';

    /* Original Logic
    if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
    if (process.env.NODE_ENV === 'production') {
        return 'https://intelligent-vitality-production.up.railway.app';
    }
    return 'http://127.0.0.1:8000';
    */
};

export const API_URL = getApiUrl();
