'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, Check, UserPlus } from 'lucide-react';
import CascadingSelector from '@/components/calculators/CascadingSelector';
import { useProfile } from '@/context/ProfileContext';

interface ProfileCreateModalProps {
    isOpen: boolean;
    onClose: () => void;
    onProfileCreated?: () => void;
}

export default function ProfileCreateModal({ isOpen, onClose, onProfileCreated }: ProfileCreateModalProps) {
    const { createProfile } = useProfile();
    const [alias, setAlias] = useState('');
    const [selection, setSelection] = useState({ company: '', group: '', level: '' });
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Reset form when modal closes
    const handleClose = () => {
        setAlias('');
        setSelection({ company: '', group: '', level: '' });
        setError(null);
        onClose();
    };

    const handleSave = async () => {
        setSaving(true);
        setError(null);
        try {
            if (!alias.trim()) {
                setError("El nombre del perfil es obligatorio.");
                setSaving(false);
                return;
            }
            if (!selection.company || !selection.group || !selection.level) {
                setError("Por favor selecciona Empresa, Grupo y Nivel.");
                setSaving(false);
                return;
            }

            await createProfile({
                alias: alias.trim(),
                company_slug: selection.company,
                job_group: selection.group,
                salary_level: selection.level,
                contract_percentage: 100,
                contract_type: 'indefinido'
            });
            if (onProfileCreated) onProfileCreated();
            handleClose();
        } catch (err: any) {
            console.error(err);
            setError(err.message || "Error al crear perfil.");
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
                        onClick={handleClose}
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
                                <UserPlus size={24} className="text-emerald-500" /> Nuevo Perfil Profesional
                            </h3>
                            <button onClick={handleClose} className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors">
                                <X size={20} />
                            </button>
                        </div>

                        <div className="space-y-4 mb-6">
                            <div>
                                <label className="text-sm font-medium text-slate-300 block mb-1">Nombre del Perfil (Alias)</label>
                                <input
                                    type="text"
                                    placeholder="Ej: Mi puesto en Iberia, Coordinación, etc."
                                    value={alias}
                                    onChange={(e) => setAlias(e.target.value)}
                                    className="w-full bg-slate-800 border border-slate-600 rounded-lg p-2 text-white focus:border-emerald-500 outline-none"
                                />
                            </div>

                            <CascadingSelector
                                onSelectionChange={(sel) => setSelection(sel)}
                            />
                        </div>

                        {error && <div className="text-red-400 text-sm mb-4 bg-red-500/10 p-2 rounded">{error}</div>}

                        <div className="flex justify-end gap-3">
                            <button
                                onClick={handleClose}
                                className="px-4 py-2 text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg flex items-center gap-2 font-medium transition-colors disabled:opacity-50"
                            >
                                {saving ? <span className="animate-spin text-white">⟳</span> : <Save size={18} />}
                                Guardar Perfil
                            </button>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
