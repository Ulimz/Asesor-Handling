'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiService, User } from '@/lib/api-service';
import { useProfile } from '@/context/ProfileContext';
import { Save, User as UserIcon, Trash2, Plus, Edit2, ShieldCheck, Check } from 'lucide-react';
import ProfileCreateModal from '@/components/profile/ProfileCreateModal';
import ProfileEditModal from '@/components/profile/ProfileEditModal';

export default function SettingsPage() {
    const router = useRouter();
    const { profiles, activeProfile, refreshProfiles, activateProfile } = useProfile();
    const [userAccount, setUserAccount] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    // Modals
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [editingProfile, setEditingProfile] = useState<any>(null); // Profile to edit

    // Account Data (Global)
    const [accountName, setAccountName] = useState('');

    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            router.push('/login');
            return;
        }
        // Load Account Data (Email, Global Name)
        apiService.getMe(token).then(u => {
            setUserAccount(u);
            setAccountName(u.preferred_name || '');
        }).catch(() => {
            // router.push('/login'); // Should we redirect? Maybe just fail silently for account data
        });
    }, [router]);

    const handleSaveAccount = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) return;
            // Update only account level fields (preferred_name in user table)
            // Note: This endpoint might update the User table, effectively setting a "default" name
            await apiService.updateProfile(token, { preferred_name: accountName });
            alert('Cuenta actualizada correctamente');
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteProfile = async (id: number) => {
        if (!confirm('¿Estás seguro de eliminar este perfil? Esta acción no se puede deshacer.')) return;
        try {
            const token = localStorage.getItem('auth_token');
            if (token) {
                await apiService.profiles.delete(token, id);
                refreshProfiles(); // Reload list
            }
        } catch (e) {
            console.error(e);
            alert("Error al eliminar perfil");
        }
    };

    return (
        <div className="p-6 md:p-10 max-w-5xl mx-auto pb-32">
            <h1 className="text-3xl font-bold text-white mb-8 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <UserIcon className="text-cyan-400" /> Configuración
                </div>
                <button
                    onClick={() => window.location.href = '/dashboard'}
                    className="text-slate-400 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-full"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
            </h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* COL 1: ACCOUNT SETTINGS */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-slate-900/50 border border-white/5 rounded-2xl p-6">
                        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                            <ShieldCheck size={20} className="text-emerald-400" /> Mi Cuenta
                        </h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs uppercase text-slate-500 font-bold mb-1">Email</label>
                                <div className="text-slate-300 font-mono text-sm bg-slate-950 p-2 rounded border border-white/5">
                                    {userAccount?.email || '...'}
                                </div>
                            </div>
                            <div>
                                <label className="block text-xs uppercase text-slate-500 font-bold mb-1">Nombre (Global)</label>
                                <input
                                    value={accountName}
                                    onChange={e => setAccountName(e.target.value)}
                                    className="w-full bg-slate-950 border border-white/10 rounded-lg p-2 text-white text-sm focus:border-cyan-500/50 outline-none"
                                />
                            </div>
                            <button
                                onClick={handleSaveAccount}
                                disabled={isLoading}
                                className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium transition-colors"
                            >
                                {isLoading ? 'Guardando...' : 'Actualizar Cuenta'}
                            </button>
                        </div>
                    </div>

                    {/* Danger Zone */}
                    <div className="bg-red-900/10 border border-red-500/20 rounded-2xl p-6">
                        <h2 className="text-sm font-bold text-red-500 mb-2 flex items-center gap-2">
                            <Trash2 size={16} /> Zona de Peligro
                        </h2>
                        <button
                            onClick={async () => {
                                if (window.confirm('¿Estás SEGURO de que quieres eliminar tu cuenta COMPLETA? Se borrarán todos tus perfiles.')) {
                                    setIsLoading(true);
                                    try {
                                        const token = localStorage.getItem('auth_token');
                                        if (token) {
                                            await apiService.deleteAccount(token);
                                            localStorage.removeItem('auth_token');
                                            window.location.href = '/';
                                        }
                                    } catch (error) {
                                        console.error(error);
                                    }
                                }
                            }}
                            className="w-full text-red-400 hover:text-white hover:bg-red-500/20 border border-red-500/30 px-4 py-2 rounded-lg transition-all text-xs"
                        >
                            Eliminar Cuenta Definitivamente
                        </button>
                    </div>
                </div>

                {/* COL 2 & 3: PROFILES */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                            <UserIcon size={20} className="text-cyan-400" /> Mis Perfiles Laborales
                        </h2>
                        <button
                            onClick={() => setIsCreateOpen(true)}
                            className="flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white px-4 py-2 rounded-xl font-medium shadow-lg shadow-cyan-900/20 transition-all transform hover:scale-105"
                        >
                            <Plus size={18} /> Nuevo Perfil
                        </button>
                    </div>

                    <div className="grid grid-cols-1 gap-4">
                        {profiles.map(profile => (
                            <div
                                key={profile.id}
                                className={`relative group p-5 rounded-2xl border transition-all ${activeProfile?.id === profile.id
                                    ? 'bg-gradient-to-br from-cyan-900/20 to-blue-900/10 border-cyan-500/50 shadow-xl shadow-cyan-900/10'
                                    : 'bg-slate-900/50 border-white/5 hover:border-white/10'
                                    }`}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="space-y-1">
                                        <div className="flex items-center gap-3">
                                            <span className="text-lg font-bold text-white">{profile.alias}</span>
                                            {activeProfile?.id === profile.id && (
                                                <span className="text-[10px] bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded-full border border-cyan-500/30 flex items-center gap-1">
                                                    <Check size={10} /> ACTIVO
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-sm text-slate-400 flex flex-col gap-0.5">
                                            <span className="capitalize text-slate-300 font-medium">{profile.company_slug.replace('-', ' ')}</span>
                                            <span>{profile.job_group} • {profile.salary_level}</span>
                                            <span className="text-xs text-slate-500">{profile.contract_percentage}% • {profile.contract_type}</span>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
                                        {activeProfile?.id !== profile.id && (
                                            <button
                                                onClick={() => activateProfile(profile.id)}
                                                className="p-2 bg-slate-800 hover:bg-cyan-600 text-slate-400 hover:text-white rounded-lg transition-colors"
                                                title="Activar este perfil"
                                            >
                                                <Check size={18} />
                                            </button>
                                        )}
                                        <button
                                            onClick={() => setEditingProfile(profile)}
                                            className="p-2 bg-slate-800 hover:bg-blue-600 text-slate-400 hover:text-white rounded-lg transition-colors"
                                            title="Editar"
                                        >
                                            <Edit2 size={18} />
                                        </button>
                                        <button
                                            onClick={() => handleDeleteProfile(profile.id)}
                                            className="p-2 bg-slate-800 hover:bg-red-600 text-slate-400 hover:text-white rounded-lg transition-colors"
                                            title="Eliminar"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}

                        {profiles.length === 0 && (
                            <div className="text-center p-12 bg-slate-900/30 border border-white/5 rounded-2xl border-dashed">
                                <UserIcon size={48} className="mx-auto text-slate-700 mb-4" />
                                <h3 className="text-slate-400 font-medium">No tienes perfiles creados</h3>
                                <p className="text-slate-500 text-sm mt-2">Crea uno para empezar a usar el asistente.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* MODALS */}
            <ProfileCreateModal
                isOpen={isCreateOpen}
                onClose={() => setIsCreateOpen(false)}
                onProfileCreated={() => {
                    setIsCreateOpen(false);
                    refreshProfiles();
                }}
            />

            {/* We need a specialized Edit modal or reuse create modal in edit mode? 
                Looking at ProfileEditModal usage in ChatInterface, it takes initialProfile and onProfileUpdated.
                But ProfileEditModal seemed to update the USER (legacy). 
                I need to check ProfileEditModal implementation. 
                If it calls apiService.updateProfile (legacy), it's WRONG for multi-profile.
                Assuming ProfileEditModal needs an update or I should use a new one.
                For now, let's assume I need to fix ProfileEditModal too if it's legacy.
            */}
            {editingProfile && (
                <ProfileEditModal
                    isOpen={!!editingProfile}
                    onClose={() => setEditingProfile(null)}
                    onProfileUpdated={(updated) => {
                        // This callback might return a user object or profile object depending on implementation.
                        // But we should just refresh profiles.
                        setEditingProfile(null);
                        refreshProfiles();
                    }}
                    initialProfile={{
                        id: editingProfile.id,
                        alias: editingProfile.alias,
                        company: editingProfile.company_slug,
                        group: editingProfile.job_group,
                        level: editingProfile.salary_level
                    }}
                // We might need to pass the ID to update a SPECIFIC profile, 
                // but ProfileEditModal likely only updates the "current" user/profile?
                // I check ProfileEditModal content in next step. If it's legacy, I will face issues.
                />
            )}
        </div >
    );
}
