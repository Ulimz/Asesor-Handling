'use client';

import { useProfile } from '@/context/ProfileContext';
import { apiService } from '@/lib/api-service';
import { useEffect, useState } from 'react';

export default function DebugPage() {
    const { profiles, activeProfile, loading, error, refreshProfiles } = useProfile();
    const [rawFetch, setRawFetch] = useState<any>(null);
    const [fetchError, setFetchError] = useState<string>("");

    // Independent fetch to bypass Context to double check
    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            apiService.profiles.getAll(token)
                .then(data => setRawFetch(data))
                .catch(err => setFetchError(err.message));
        }
    }, []);

    return (
        <div className="p-8 text-white space-y-6">
            <h1 className="text-2xl font-bold text-red-400">🚨 PÁGINA DE DIAGNÓSTICO</h1>

            <div className="bg-slate-900 p-4 rounded border border-slate-700">
                <h2 className="text-xl font-bold mb-2">1. Estado del Contexto (ProfileContext)</h2>
                <div className="font-mono text-sm">
                    <p>Loading: {loading ? "TRUE" : "FALSE"}</p>
                    <p>Error: {error || "NONE"}</p>
                    <p>Profiles Count: {profiles.length}</p>
                    <p>Active Profile: {activeProfile ? activeProfile.alias : "NULL"}</p>
                </div>
            </div>

            <div className="bg-slate-900 p-4 rounded border border-slate-700">
                <h2 className="text-xl font-bold mb-2">2. JSON de Perfiles (Contexto)</h2>
                <pre className="bg-black p-2 rounded overflow-auto max-h-40 text-xs">
                    {JSON.stringify(profiles, null, 2)}
                </pre>
            </div>

            <div className="bg-slate-900 p-4 rounded border border-slate-700">
                <h2 className="text-xl font-bold mb-2">3. Fetch Directo (Bypassing Context)</h2>
                {fetchError && <p className="text-red-500">Error: {fetchError}</p>}
                <pre className="bg-black p-2 rounded overflow-auto max-h-40 text-xs text-green-400">
                    {JSON.stringify(rawFetch, null, 2)}
                </pre>
            </div>

            <button
                onClick={refreshProfiles}
                className="bg-blue-600 px-4 py-2 rounded text-white"
            >
                Forzar Recarga (RefreshProfiles)
            </button>
        </div>
    );
}
