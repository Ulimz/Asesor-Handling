'use client';

import { useState, useEffect } from 'react';
import { apiService } from '@/lib/api-service';
import CompanyDropdown from '@/components/CompanyDropdown';
import MobileNav from '@/components/MobileNav';
import ChatInterface from "@/components/ChatInterface";
import SalaryCalculator from '@/features/calculadoras/components/SalaryCalculator';
import AlertsPanel from '@/components/alerts/AlertsPanel';
import ClaimGenerator from '@/components/claims/ClaimGenerator';
import { CompanyId, companies } from '@/data/knowledge-base';
import { type KnowledgeItem } from '@/data/knowledge-base';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Calculator, Settings, LogOut, User, Bell, PenTool, Loader2, Plane } from 'lucide-react';
import { useRouter } from 'next/navigation';
import NeonLogo from '@/components/NeonLogo';
import Image from 'next/image';
import BrandLogo from '@/components/BrandLogo';
import ThemeToggle from '@/components/ThemeToggle';

export default function DashboardPage() {
    const router = useRouter();
    const [selectedCompanyId, setSelectedCompanyId] = useState<CompanyId | null>(null);
    const [activeTab, setActiveTab] = useState<'chat' | 'calculator' | 'alerts' | 'claims'>('chat');
    const [isAuthorized, setIsAuthorized] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            router.push('/login');
            return;
        }

        // Verify profile completeness
        apiService.getMe(token)
            .then(user => {
                if (!user.company_slug) {
                    router.push('/onboarding');
                } else {
                    setIsAuthorized(true);
                    if (user.company_slug) setSelectedCompanyId(user.company_slug as any);
                }
            })
            .catch(() => router.push('/login'));
    }, [router]);

    if (!isAuthorized) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
            </div>
        );
    }

    const handleCompanySelect = (companyId: CompanyId) => {
        setSelectedCompanyId(companyId);
    };

    const handleLogout = () => {
        localStorage.removeItem('auth_token');
        router.push('/');
    };

    const selectedCompanyName = companies.find(c => c.id === selectedCompanyId)?.name;

    return (
        <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] font-sans selection:bg-cyan-500/30 transition-colors duration-300">
            {/* Background Effects */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-cyan-500/10 rounded-full blur-[100px] animate-pulse-slow"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[100px] animate-pulse-slow delay-1000"></div>
            </div>

            <div className="relative z-10 flex h-screen overflow-hidden">

                {/* SIDEBAR (Desktop) */}
                <aside className="hidden md:flex flex-col w-20 lg:w-64 glass-panel border-r border-[var(--panel-border)] transition-colors duration-300">
                    <div className="p-6 flex items-center justify-center border-b border-white/5">
                        <BrandLogo iconSize={64} textSize="lg" />
                    </div>

                    <nav className="flex-1 px-4 py-6 space-y-2">
                        <button
                            onClick={() => setActiveTab('chat')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'chat' ? 'bg-[var(--panel-bg)] text-[var(--text-primary)] shadow-lg shadow-black/5 border border-[var(--panel-border)]' : 'text-[var(--text-secondary)] hover:bg-[var(--panel-bg)]/50 hover:text-[var(--text-primary)]'}`}
                        >
                            <MessageSquare size={20} />
                            <span className="hidden lg:block">Chat Asistente</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('calculator')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'calculator' ? 'bg-gradient-to-r from-emerald-500/20 to-green-500/10 border border-emerald-500/20 text-emerald-500 dark:text-emerald-400 shadow-lg shadow-emerald-500/10' : 'text-[var(--text-secondary)] hover:bg-[var(--panel-bg)]/50 hover:text-[var(--text-primary)]'}`}
                        >
                            <Calculator size={20} />
                            <span className="hidden lg:block">Calculadora</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('claims')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'claims' ? 'bg-indigo-500/10 text-indigo-500 dark:text-indigo-400 border border-indigo-500/20 shadow-lg shadow-indigo-500/10' : 'text-[var(--text-secondary)] hover:bg-[var(--panel-bg)]/50 hover:text-[var(--text-primary)]'}`}
                        >
                            <PenTool size={20} />
                            <span className="hidden lg:block">Reclamaciones</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('alerts')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'alerts' ? 'bg-amber-500/10 text-amber-500 dark:text-amber-400 border border-amber-500/20 shadow-lg shadow-amber-500/10' : 'text-[var(--text-secondary)] hover:bg-[var(--panel-bg)]/50 hover:text-[var(--text-primary)]'}`}
                        >
                            <Bell size={20} />
                            <span className="hidden lg:block">Novedades</span>
                        </button>
                    </nav>

                    <div className="p-4 border-t border-white/5 space-y-2">
                        <button
                            onClick={() => router.push('/dashboard/settings')}
                            className="flex items-center gap-3 w-full px-4 py-3 text-slate-400 hover:text-white transition-colors"
                        >
                            <Settings size={20} />
                            <span className="hidden lg:block">Configuración</span>
                        </button>
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-3 w-full px-4 py-3 text-slate-400 hover:text-red-400 transition-colors"
                        >
                            <LogOut size={20} />
                            <span className="hidden lg:block">Cerrar Sesión</span>
                        </button>
                    </div>
                </aside>

                {/* MAIN CONTENT */}
                <main className="flex-1 flex flex-col h-full bg-slate-950/50 relative min-w-0">
                    {/* Header */}
                    <header className="relative h-16 px-6 border-b border-[var(--panel-border)] flex items-center justify-between bg-[var(--bg-primary)]/80 backdrop-blur-md z-20 transition-colors duration-300">
                        {/* LEFT: Placeholder - Hidden on mobile to save space */}
                        <div className="hidden md:flex items-center gap-4 w-20">
                        </div>

                        {/* CENTER: Title - Flex 1 to take available space and center within it */}
                        <div className="flex-1 flex justify-center items-center overflow-hidden px-2">
                            <h1 className="text-lg md:text-xl font-semibold text-white whitespace-nowrap truncate">
                                {activeTab === 'chat' && (
                                    <span className="tracking-widest drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">
                                        AS
                                        <span className="text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]">I</span>
                                        STENTE
                                        {' '}
                                        H
                                        <span className="text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]">A</span>
                                        NDLING
                                    </span>
                                )}
                                {activeTab === 'calculator' && 'Herramientas de Nómina'}
                                {activeTab === 'alerts' && 'Centro de Novedades'}
                                {activeTab === 'claims' && 'Generador de Escritos'}
                            </h1>
                        </div>

                        {/* RIGHT: User Profile & Company */}
                        <div className="flex items-center gap-4">
                            <div className="md:hidden">
                                <ThemeToggle />
                            </div>
                            <CompanyDropdown
                                onSelect={handleCompanySelect}
                                selectedCompanyId={selectedCompanyId}
                            />
                            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-500 p-[1px] shadow-lg shadow-cyan-500/20">
                                <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center">
                                    <User size={20} className="text-slate-400" />
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* Content Area */}
                    <div className="flex-1 overflow-hidden relative p-4 md:p-6 min-w-0">
                        <AnimatePresence mode="wait">
                            {activeTab === 'chat' && (
                                <motion.div
                                    key="chat"
                                    initial={{ opacity: 0, scale: 0.98 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.98 }}
                                    transition={{ duration: 0.2 }}
                                    className="h-full w-full"
                                >
                                    <ChatInterface key={selectedCompanyId} selectedCompanyId={selectedCompanyId} /> {/* Key forces reset on company change */}
                                </motion.div>
                            )}

                            {activeTab === 'calculator' && (
                                <motion.div
                                    key="calculator"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    transition={{ duration: 0.2 }}
                                    className="h-full overflow-y-auto p-6 pb-28 md:pb-6"
                                >
                                    <SalaryCalculator />
                                </motion.div>
                            )}

                            {activeTab === 'claims' && (
                                <motion.div
                                    key="claims"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    transition={{ duration: 0.2 }}
                                    className="h-full overflow-y-auto p-6 pb-28 md:pb-6"
                                >
                                    <ClaimGenerator />
                                </motion.div>
                            )}

                            {activeTab === 'alerts' && (
                                <motion.div
                                    key="alerts"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    transition={{ duration: 0.2 }}
                                    className="h-full overflow-y-auto p-6 pb-28 md:pb-6"
                                >
                                    <AlertsPanel />
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </main>
            </div >

            <MobileNav activeTab={activeTab} setActiveTab={setActiveTab} />
        </div >
    );
}
