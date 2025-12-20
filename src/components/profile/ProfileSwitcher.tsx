'use client';

import { useState } from 'react';
import { useProfile } from '@/context/ProfileContext';
import { User, ChevronDown, Check, Plus, Briefcase, Building2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ProfileCreateModal from './ProfileCreateModal';
import { companies, getCompanyById } from '@/data/knowledge-base';

export default function ProfileSwitcher() {
    const { profiles, activeProfile, activateProfile, loading } = useProfile();
    const [isOpen, setIsOpen] = useState(false);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    if (loading && profiles.length === 0) return <div className="w-8 h-8 rounded-full bg-slate-800 animate-pulse"></div>;

    // If no profiles, show Create Button directly? Or empty state.

    const activeCompany = activeProfile ? getCompanyById(activeProfile.company_slug) : null;

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/5 transition-colors border border-transparent hover:border-white/10"
            >
                <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs shadow-lg border border-white/10"
                    style={{ backgroundColor: activeCompany ? activeCompany.color : '#334155' }}
                >
                    {activeCompany ? activeCompany.name.charAt(0) : <Briefcase size={14} />}
                </div>
                <div className="block text-left">
                    <div className="text-xs text-slate-400 hidden md:block">Perfil Activo</div>
                    <div className="text-sm font-medium text-white max-w-[100px] md:max-w-[150px] truncate">
                        {activeProfile ? activeProfile.alias : 'Sin Perfil'}
                    </div>
                </div>
                <ChevronDown size={14} className={`text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            <AnimatePresence>
                {isOpen && (
                    <>
                        {/* Backdrop to close */}
                        <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />

                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 10 }}
                            className="absolute right-0 top-full mt-2 w-64 bg-slate-900 border border-slate-700 rounded-xl shadow-xl z-50 overflow-hidden"
                        >
                            <div className="p-2 border-b border-white/5">
                                <div className="text-xs font-semibold text-slate-500 px-2 py-1 uppercase tracking-wider">Mis Perfiles</div>
                            </div>

                            <div className="max-h-[300px] overflow-y-auto">
                                {profiles.length === 0 ? (
                                    <div className="p-4 text-center text-sm text-slate-500">No tienes perfiles creados</div>
                                ) : (
                                    profiles.map(profile => (
                                        <button
                                            key={profile.id}
                                            onClick={() => {
                                                activateProfile(profile.id);
                                                setIsOpen(false);
                                            }}
                                            className={`w-full text-left p-3 hover:bg-white/5 flex items-center gap-3 transition-colors ${activeProfile?.id === profile.id ? 'bg-emerald-500/10' : ''}`}
                                        >
                                            <div className={`w-2 h-2 rounded-full ${activeProfile?.id === profile.id ? 'bg-emerald-500' : 'bg-slate-600'}`} />
                                            <div className="flex-1 min-w-0">
                                                <div className={`text-sm font-medium ${activeProfile?.id === profile.id ? 'text-emerald-400' : 'text-slate-200'} truncate`}>
                                                    {profile.alias}
                                                </div>
                                                <div className="text-xs text-slate-500 truncate">
                                                    {profile.company_slug} • {profile.job_group}
                                                </div>
                                            </div>
                                            {activeProfile?.id === profile.id && <Check size={14} className="text-emerald-500" />}
                                        </button>
                                    ))
                                )}
                            </div>

                            {/* Create Profile button removed as per user request */}
                        </motion.div>
                    </>
                )}
            </AnimatePresence>

            <ProfileCreateModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
            />
        </div>
    );
}
