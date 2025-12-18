'use client';

import { useState, useEffect } from 'react';
import { apiService } from '@/lib/api-service';
import ProfileSwitcher from '@/components/profile/ProfileSwitcher';
import { useProfile } from '@/context/ProfileContext';
import dynamic from 'next/dynamic';

import ChatInterface from "@/components/ChatInterface";

import { CompanyId, companies, getCompanyById } from '@/data/knowledge-base';
import { type KnowledgeItem } from '@/data/knowledge-base';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Calculator, Settings, LogOut, User, Bell, PenTool, Loader2, Plane, Menu, X, Download } from 'lucide-react';
import { AlertTriangle, Info, CheckCircle, FileText, Gavel, Scale, Briefcase } from 'lucide-react';
import Link from 'next/link';
import MobileMenu from '@/components/MobileMenu';

// Dynamic Imports
const SalaryCalculator = dynamic(() => import('@/features/calculadoras/components/SalaryCalculator'), {
    loading: () => <div className="h-full flex items-center justify-center"><Loader2 className="w-8 h-8 text-cyan-500 animate-spin" /></div>
});

const ClaimGenerator = dynamic(() => import('@/components/claims/ClaimGenerator'), {
    loading: () => <div className="h-full flex items-center justify-center"><Loader2 className="w-8 h-8 text-cyan-500 animate-spin" /></div>
});

const AlertsPanel = dynamic(() => import('@/components/alerts/AlertsPanel'), {
    loading: () => <div className="h-full flex items-center justify-center"><Loader2 className="w-8 h-8 text-cyan-500 animate-spin" /></div>
});


export default function DashboardPage() {
    const { activeProfile } = useProfile();
    const [activeTab, setActiveTab] = useState<'chat' | 'calculator' | 'alerts' | 'claims'>('chat');
    const [selectedCompany, setSelectedCompany] = useState<CompanyId | null>(null);
    const [showMobileMenu, setShowMobileMenu] = useState(false);

    // Sync Local State with Profile Context
    useEffect(() => {
        if (activeProfile && activeProfile.company_slug) {
            setSelectedCompany(activeProfile.company_slug as CompanyId);
        }
    }, [activeProfile]);

    const renderContent = () => {
        switch (activeTab) {
            case 'chat':
                return <ChatInterface selectedCompanyId={selectedCompany} />;
            case 'calculator':
                return <SalaryCalculator />;
            case 'alerts':
                return <AlertsPanel />;
            case 'claims':
                return <ClaimGenerator />;
            default:
                return <ChatInterface selectedCompanyId={selectedCompany} />;
        }
    };

    return (
        <div className="flex flex-col h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] overflow-hidden transition-colors duration-300">
            {/* Header */}
            <header className="flex-none h-16 border-b border-[var(--border-primary)] bg-[var(--panel-bg)]/80 backdrop-blur-xl px-4 flex items-center justify-between z-30 transition-colors duration-300">
                <div className="flex items-center gap-4">
                    <div className="bg-gradient-to-tr from-cyan-500 to-blue-600 p-2 rounded-xl shadow-lg shadow-cyan-500/20">
                        <Plane className="text-white transform -rotate-45" size={20} />
                    </div>
                    <div>
                        <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                            Asesor Handling
                        </h1>
                        <span className="text-[10px] uppercase tracking-widest text-cyan-500 font-semibold">AI Assistant</span>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {/* DESKTOP HEADER ITEMS */}
                    <div className="hidden md:flex items-center gap-3">
                        <ProfileSwitcher />
                        <div className="h-8 w-[1px] bg-[var(--border-secondary)] mx-2"></div>
                        <button className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--hover-bg)] rounded-full transition-all">
                            <Bell size={20} />
                        </button>
                        <Link href="/dashboard/settings">
                            <button className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--hover-bg)] rounded-full transition-all">
                                <Settings size={20} />
                            </button>
                        </Link>
                    </div>

                    {/* MOBILE MENU TOGGLE */}
                    <button
                        onClick={() => setShowMobileMenu(true)}
                        className="md:hidden p-2 text-[var(--text-secondary)] hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                        <Menu size={24} />
                    </button>
                </div>
            </header>

            {/* Mobile Menu Overlay */}
            <AnimatePresence>
                {showMobileMenu && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowMobileMenu(false)}
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
                                    onClick={() => setShowMobileMenu(false)}
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
                                        onClick={() => { setActiveTab('chat'); setShowMobileMenu(false); }}
                                        className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'chat' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'text-[var(--text-secondary)] hover:bg-[var(--hover-bg)]'}`}
                                    >
                                        <MessageSquare size={18} /> Chat Asistente
                                    </button>
                                    <button
                                        onClick={() => { setActiveTab('calculator'); setShowMobileMenu(false); }}
                                        className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'calculator' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-[var(--text-secondary)] hover:bg-[var(--hover-bg)]'}`}
                                    >
                                        <Calculator size={18} /> Calculadora Nómina
                                    </button>
                                    <button
                                        onClick={() => { setActiveTab('alerts'); setShowMobileMenu(false); }}
                                        className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'alerts' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'text-[var(--text-secondary)] hover:bg-[var(--hover-bg)]'}`}
                                    >
                                        <AlertTriangle size={18} /> Alertas Legales
                                    </button>
                                    <button
                                        onClick={() => { setActiveTab('claims'); setShowMobileMenu(false); }}
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
                                    {/* Mobile Profile Switcher might duplicate UI, but sticking to existing pattern */}

                                    <Link href="/dashboard/settings" onClick={() => setShowMobileMenu(false)}>
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
                    </>
                )}
            </AnimatePresence>

            {/* Main Content Area */}
            <main className="flex-1 overflow-hidden relative">
                {renderContent()}
            </main>
        </div>
    );
}
