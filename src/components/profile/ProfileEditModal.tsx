'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, Check } from 'lucide-react';
import CascadingSelector from '@/components/calculators/CascadingSelector';
import { apiService } from '@/lib/api-service';

interface ProfileEditModalProps {
    isOpen: boolean;
    onClose: () => void;
    onProfileUpdated: (user: any) => void;
    initialProfile?: {
        company: string;
        group: string;
        level: string;
    };
}

export default function ProfileEditModal({ isOpen, onClose, onProfileUpdated, initialProfile }: ProfileEditModalProps) {
    const [selection, setSelection] = useState(initialProfile || { company: '', group: '', level: '' });
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSave = async () => {
        setSaving(true);
        setError(null);
        try {
            const token = localStorage.getItem('auth_token');
            if (token && selection.company && selection.group && selection.level) {
                const updatedUser = await apiService.updateProfile(token, {
                    company_slug: selection.company,
                    job_group: selection.group,
                    salary_level: selection.level
                });
                onProfileUpdated(updatedUser);
                onClose();
            } else {
                setError("Please select all fields.");
            }
        } catch (err) {
            console.error(err);
            setError("Failed to save profile.");
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
                            <h3 className="text-xl font-bold text-white">Edit User Profile</h3>
                            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors">
                                <X size={20} />
                            </button>
                        </div>

                        <div className="mb-6">
                            <CascadingSelector
                                initialSelection={initialProfile}
                                onSelectionChange={(sel) => setSelection(sel)}
                            />
                        </div>

                        {error && <div className="text-red-400 text-sm mb-4">{error}</div>}

                        <div className="flex justify-end gap-3">
                            <button
                                onClick={onClose}
                                className="px-4 py-2 text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg flex items-center gap-2 font-medium transition-colors disabled:opacity-50"
                            >
                                {saving ? <span className="animate-spin text-white">⟳</span> : <Save size={18} />}
                                Save Profile
                            </button>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
