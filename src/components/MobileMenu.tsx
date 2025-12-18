'use client';

// MobileMenu.tsx - Extracted from DashboardPage for modularity

import { motion, AnimatePresence } from 'framer-motion';
import { X, MessageSquare, Calculator, Settings, LogOut, Bell, AlertTriangle, Gavel } from 'lucide-react';
import { CompanyId, getCompanyById } from '@/data/knowledge-base';
import ProfileSwitcher from '@/components/profile/ProfileSwitcher';
import Link from 'next/link';

interface MobileMenuProps {
    show: boolean;
    onClose: () => void;
    activeProfile: any;
    activeTab: string;
    setActiveTab: (tab: any) => void;
}

export default function MobileMenu({ show, onClose, activeProfile, activeTab, setActiveTab }: MobileMenuProps) {
    if (!show) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={onClose}
                className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
            />
            <motion.div
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                transition={{ type: "spring", damping: 25, stiffness: 200 }}
                className="fixed inset-y-0 right-0 w-[85vw] max-w-sm bg-[var(--panel-bg)] border-l border-[var(--border-primary)] shadow-2xl z-50 md:hidden flex flex-col"
            >
                <div className="p-4 border-b border-[var(--border-primary)] flex justify-between items-center bg-[var(--panel-bg)]">
                    <span className="font-bold text-lg text-[var(--text-primary)]">Menú</span>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-[var(--hover-bg)] rounded-full text-[var(--text-secondary)] transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-6">
                    {/* MOBILE PROFILE CARD */}
                    {activeProfile && (
                        <div className="mb-6">
                            <div className="text-[10px] font-bold text-[var(--text-secondary)] uppercase tracking-widest mb-2 px-1">
                                Perfil Activo
                            </div>
                            <div className="p-3 bg-[var(--panel-bg)] rounded-xl border border-[var(--panel-border)] flex items-center gap-3">
                                <div
                                    className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-sm"
                                    style={{ backgroundColor: getCompanyById(activeProfile.company_slug)?.color || '#334155' }}
                                >
                                    {getCompanyById(activeProfile.company_slug)?.name.charAt(0) || 'E'}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="text-sm font-semibold text-white truncate">{activeProfile.alias}</div>
                                    <div className="text-xs text-[var(--text-secondary)] truncate">
                                        {getCompanyById(activeProfile.company_slug)?.agreementLabel || activeProfile.company_slug}
                                    </div>
                                    <div className="text-[10px] text-cyan-400 mt-0.5 font-medium uppercase tracking-wide">
                                        {activeProfile.job_group} • {activeProfile.salary_level}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="space-y-1">
                        <div className="text-[10px] font-bold text-[var(--text-secondary)] uppercase tracking-widest mb-2 px-1">
                            Herramientas
                        </div>
                        <button
                            onClick={() => { setActiveTab('chat'); onClose(); }}
                            className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'chat' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'text-[var(--text-secondary)] hover:bg-[var(--hover-bg)]'}`}
                        >
                            <MessageSquare size={18} /> Chat Asistente
                        </button>
                        <button
                            onClick={() => { setActiveTab('calculator'); onClose(); }}
                            className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'calculator' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-[var(--text-secondary)] hover:bg-[var(--hover-bg)]'}`}
                        >
                            <Calculator size={18} /> Calculadora Nómina
                        </button>
                        <button
                            onClick={() => { setActiveTab('alerts'); onClose(); }}
                            className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'alerts' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'text-[var(--text-secondary)] hover:bg-[var(--hover-bg)]'}`}
                        >
                            <AlertTriangle size={18} /> Alertas Legales
                        </button>
                        <button
                            onClick={() => { setActiveTab('claims'); onClose(); }}
                            className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'claims' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' : 'text-[var(--text-secondary)] hover:bg-[var(--hover-bg)]'}`}
                        >
                            <Gavel size={18} /> Generador Reclamaciones
                        </button>
                    </div>

                    <div className="pt-4 border-t border-[var(--border-primary)] space-y-1">
                        <div className="text-[10px] font-bold text-[var(--text-secondary)] uppercase tracking-widest mb-2 px-1">
                            Sistema
                        </div>
                        <ProfileSwitcher />

                        <Link href="/dashboard/settings" onClick={onClose}>
                            <button className="w-full flex items-center gap-3 p-3 rounded-xl text-[var(--text-secondary)] hover:bg-[var(--hover-bg)] transition-all">
                                <Settings size={18} /> Configuración
                            </button>
                        </Link>
                        <button className="w-full flex items-center gap-3 p-3 rounded-xl text-red-400 hover:bg-red-500/10 transition-all">
                            <LogOut size={18} /> Cerrar Sesión
                        </button>
                    </div>
                </div>
            </motion.div>
        </AnimatePresence>
    );
}
