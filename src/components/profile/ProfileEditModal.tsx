'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, Edit } from 'lucide-react';
import CascadingSelector from '@/components/calculators/CascadingSelector';
import { apiService } from '@/lib/api-service';

interface ProfileEditModalProps {
    isOpen: boolean;
    onClose: () => void;
    onProfileUpdated: (updatedProfile: any) => void;
    initialProfile: {
        id?: number; // Should be mandatory for editing specific profiles, optional if used for legacy user?? keeping optional for safety but logic requires it
        alias?: string;
        company: string;
        group: string;
        level: string;
    };
}

export default function ProfileEditModal({ isOpen, onClose, onProfileUpdated, initialProfile }: ProfileEditModalProps) {
    const [alias, setAlias] = useState(initialProfile?.alias || '');
    const [selection, setSelection] = useState({
        company: initialProfile?.company || '',
        group: initialProfile?.group || '',
        level: initialProfile?.level || ''
    });
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSave = async () => {
        setSaving(true);
        setError(null);
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) return;

            // If we have an ID, we update a Profile. If NOT, we assume legacy User update?
            // Given the new architecture, we should always update a profile if called from Settings.
            // But ChatInterface might call it with "user" data which doesn't have ID.
            // If ID is missing, we can't update a profile.

            if (initialProfile.id) {
                if (!alias.trim()) throw new Error("El alias es obligatorio.");

                const updatedData = {
                    alias: alias,
                    company_slug: selection.company,
                    job_group: selection.group,
                    salary_level: selection.level
                };

                const res = await apiService.profiles.update(token, initialProfile.id, updatedData);
                onProfileUpdated(res);
                onClose();
            } else {
                // Fallback: Legacy User Update (only for company/group/level, no alias)
                // This shouldn't be used ideally, but preventing crash.
                console.warn("ProfileEditModal: No Profile ID provided. Attempting legacy update.");
                const updatedUser = await apiService.updateProfile(token, {
                    company_slug: selection.company,
                    job_group: selection.group,
                    salary_level: selection.level
                });
                onProfileUpdated(updatedUser);
                onClose();
            }
        } catch (err: any) {
            console.error(err);
            setError(err.message || "Error al actualizar perfil.");
        } finally {
            setSaving(false);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                        onClick={onClose}
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl z-50 p-6"
                    >
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Edit size={24} className="text-blue-500" /> Editar Perfil
                            </h3>
                            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors">
                                <X size={20} />
                            </button>
                        </div>

                        <div className="space-y-4 mb-6">
                            {initialProfile.id && (
                                <div>
                                    <label className="text-sm font-medium text-slate-300 block mb-1">Nombre (Alias)</label>
                                    <input
                                        value={alias}
                                        onChange={(e) => setAlias(e.target.value)}
                                        className="w-full bg-slate-800 border border-slate-600 rounded-lg p-2 text-white focus:border-blue-500 outline-none"
                                        placeholder="Ej. Mi puesto principal"
                                    />
                                </div>
                            )}

                            <CascadingSelector
                                initialSelection={{
                                    company: selection.company,
                                    group: selection.group,
                                    level: selection.level
                                }}
                                onSelectionChange={(sel) => setSelection(sel)}
                            />
                        </div>

                        {error && <div className="text-red-400 text-sm mb-4 bg-red-500/10 p-2 rounded">{error}</div>}

                        <div className="flex justify-end gap-3">
                            <button
                                onClick={onClose}
                                className="px-4 py-2 text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 font-medium transition-colors disabled:opacity-50"
                            >
                                {saving ? <span className="animate-spin text-white">⟳</span> : <Save size={18} />}
                                Guardar Cambios
                            </button>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
