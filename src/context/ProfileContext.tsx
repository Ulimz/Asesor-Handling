'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '@/lib/api-service';

export interface Profile {
    id: number;
    alias: string;
    company_slug: string;
    job_group: string;
    salary_level: string;
    contract_percentage: number;
    contract_type: string;
    is_active: boolean;
}

interface ProfileContextType {
    profiles: Profile[];
    activeProfile: Profile | null;
    loading: boolean;
    error: string | null;
    refreshProfiles: () => Promise<void>;
    createProfile: (data: Omit<Profile, 'id' | 'is_active'>) => Promise<void>;
    activateProfile: (id: number) => Promise<void>;
    deleteProfile: (id: number) => Promise<void>;
    updateProfile: (id: number, data: Partial<Profile>) => Promise<void>;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

export function ProfileProvider({ children }: { children: React.ReactNode }) {
    const [profiles, setProfiles] = useState<Profile[]>([]);
    const [activeProfile, setActiveProfile] = useState<Profile | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const refreshProfiles = async () => {
        const token = localStorage.getItem('auth_token');
        if (!token) return;

        try {
            setLoading(true);
            const data = await apiService.profiles.getAll(token);
            setProfiles(data);
            const active = data.find((p: Profile) => p.is_active) || data[0] || null;
            setActiveProfile(active);
            setError(null);
        } catch (err: any) {
            console.error(err);
            // Don't set global error to avoid blocking UI if just no profiles
        } finally {
            setLoading(false);
        }
    };

    const createProfile = async (data: any) => {
        const token = localStorage.getItem('auth_token');
        if (!token) return;
        try {
            await apiService.profiles.create(token, data);
            await refreshProfiles();
        } catch (err: any) {
            setError(err.message || "Failed to create profile");
            throw err;
        }
    };

    const activateProfile = async (id: number) => {
        const token = localStorage.getItem('auth_token');
        if (!token) return;
        try {
            await apiService.profiles.activate(token, id);
            await refreshProfiles();
        } catch (err: any) {
            setError(err.message);
        }
    };

    const deleteProfile = async (id: number) => {
        const token = localStorage.getItem('auth_token');
        if (!token) return;
        try {
            await apiService.profiles.delete(token, id);
            await refreshProfiles();
        } catch (err: any) {
            setError(err.message);
        }
    };

    const updateProfile = async (id: number, data: any) => {
        const token = localStorage.getItem('auth_token');
        if (!token) return;
        try {
            await apiService.profiles.update(token, id, data);
            await refreshProfiles();
        } catch (err: any) {
            setError(err.message);
        }
    };

    // Initial load
    useEffect(() => {
        refreshProfiles();
    }, []);

    return (
        <ProfileContext.Provider value={{
            profiles,
            activeProfile,
            loading,
            error,
            refreshProfiles,
            createProfile,
            activateProfile,
            deleteProfile,
            updateProfile
        }}>
            {children}
        </ProfileContext.Provider>
    );
}

export function useProfile() {
    const context = useContext(ProfileContext);
    if (context === undefined) {
        throw new Error('useProfile must be used within a ProfileProvider');
    }
    return context;
}
