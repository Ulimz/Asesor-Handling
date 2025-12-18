'use client';

import { useState, useEffect } from 'react';
import { apiService } from '@/lib/api-service';
import CompanyBadge from '@/components/CompanyBadge';
import ProfileSwitcher from '@/components/profile/ProfileSwitcher';
import { useProfile } from '@/context/ProfileContext';
import dynamic from 'next/dynamic';

import ChatInterface from "@/components/ChatInterface";
// Static imports removed to optimize initial bundle size
// import SalaryCalculator from '@/features/calculadoras/components/SalaryCalculator';
// import AlertsPanel from '@/components/alerts/AlertsPanel';
// import ClaimGenerator from '@/components/claims/ClaimGenerator';

const SalaryCalculator = dynamic(() => import('@/features/calculadoras/components/SalaryCalculator'), {
    loading: () => <div className="h-full flex items-center justify-center"><Loader2 className="w-8 h-8 text-cyan-500 animate-spin" /></div>
});

const ClaimGenerator = dynamic(() => import('@/components/claims/ClaimGenerator'), {
    loading: () => <div className="h-full flex items-center justify-center"><Loader2 className="w-8 h-8 text-cyan-500 animate-spin" /></div>
});

const AlertsPanel = dynamic(() => import('@/components/alerts/AlertsPanel'), {
    loading: () => <div className="h-full flex items-center justify-center"><Loader2 className="w-8 h-8 text-cyan-500 animate-spin" /></div>
});

import { CompanyId, companies } from '@/data/knowledge-base';
import { type KnowledgeItem } from '@/data/knowledge-base';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Calculator, Settings, LogOut, User, Bell, PenTool, Loader2, Plane, Menu, X, Download } from 'lucide-react';
import { useRouter } from 'next/navigation';
import NeonLogo from '@/components/NeonLogo';
import Image from 'next/image';
import BrandLogo from '@/components/BrandLogo';
import ThemeToggle from '@/components/ThemeToggle';
import PwaInstallGuide from '@/components/pwa/PwaInstallGuide';

export default function DashboardPage() {
    const router = useRouter();
    const { activeProfile, loading: profileLoading } = useProfile();
    const [selectedCompanyId, setSelectedCompanyId] = useState<CompanyId | null>(null);
    const [activeTab, setActiveTab] = useState<'chat' | 'calculator' | 'alerts' | 'claims'>('chat');
    const [isAuthorized, setIsAuthorized] = useState(false);

    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [showInstallGuide, setShowInstallGuide] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            router.push('/login');
            return;
        }

        // Verify profile completeness
        apiService.getMe(token)
            .then(user => {
                // With multi-profile, we check if they have at least one profile or require onboarding?
                // For now, allow access if token is valid.
                setIsAuthorized(true);
                // Fallback to user's legacy company if no profile active yet
                if (user.company_slug && !selectedCompanyId) setSelectedCompanyId(user.company_slug as any);
            })
            .catch(() => router.push('/login'));
    }, [router]);

    // Sync selected company with active profile
    useEffect(() => {
        if (activeProfile) {
            setSelectedCompanyId(activeProfile.company_slug as CompanyId);
        }
    }, [activeProfile]);

    if (!isAuthorized) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
            </div>
        );
    }

    if (!isAuthorized) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
            </div>
        );
    }

    const handleLogout = () => {
        localStorage.removeItem('auth_token');
        router.push('/');
    };

    const selectedCompanyName = companies.find(c => c.id === selectedCompanyId)?.name;

    const navItems = [
        { id: 'chat' as const, label: 'Chat Asistente', icon: MessageSquare },
        { id: 'calculator' as const, label: 'Calculadora', icon: Calculator },
        { id: 'claims' as const, label: 'Reclamaciones', icon: PenTool },
        { id: 'alerts' as const, label: 'Novedades', icon: Bell },
    ];

    return (
        <div className="fixed inset-0 md:static md:h-screen w-full bg-[var(--bg-primary)] text-[var(--text-primary)] font-sans selection:bg-cyan-500/30 transition-colors duration-300 overflow-hidden flex flex-col">
            {/* Background Effects */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-cyan-500/10 rounded-full blur-[100px] animate-pulse-slow"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[100px] animate-pulse-slow delay-1000"></div>
            </div>

            <div className="relative z-10 flex h-full overflow-hidden">

                {/* SIDEBAR (Desktop) */}
                <aside className="hidden md:flex flex-col w-20 lg:w-64 glass-panel border-r border-[var(--panel-border)] transition-colors duration-300">
                    <div className="p-6 flex items-center justify-center border-b border-white/5">
                        <BrandLogo iconSize={64} textSize="lg" />
                    </div>

                    <nav className="flex-1 px-4 py-6 space-y-2">
                        {navItems.map(item => (
                            <button
                                key={item.id}
                                onClick={() => setActiveTab(item.id)}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === item.id ? 'bg-[var(--panel-bg)] text-[var(--text-primary)] shadow-lg shadow-black/5 border border-[var(--panel-border)]' : 'text-[var(--text-secondary)] hover:bg-[var(--panel-bg)]/50 hover:text-[var(--text-primary)]'}`}
                            >
                                <item.icon size={20} />
                                <span className="hidden lg:block">{item.label}</span>
                            </button>
                        ))}
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
                <main className="flex-1 flex flex-col h-full bg-[var(--bg-primary)]/50 relative min-w-0">
                    {/* Header */}
                    <header className="relative h-16 md:h-20 px-4 md:px-6 border-b border-[var(--panel-border)] flex items-center justify-between bg-[var(--bg-primary)]/80 backdrop-blur-md z-30 transition-colors duration-300">

                        {/* LEFT: Logo & Company (Mobile Optimized) */}
                        <div className="flex items-center gap-3 md:gap-6 flex-1 min-w-0">
                            {/* Logo */}
                            <div className="shrink-0 md:hidden">
                                <BrandLogo iconSize={40} showText={true} textSize="sm" />
                            </div>



                            {/* Company Icon (Static Badge) */}
                            <div className="md:hidden shrink-0">
                                <CompanyBadge
                                    companyId={selectedCompanyId}
                                    showName={false}
                                />
                            </div>
                            {/* Desktop Title */}
                            <div className="hidden md:block">
                                <h1 className="text-xl font-semibold text-white whitespace-nowrap truncate">
                                    {activeTab === 'chat' && 'CHAT IA'}
                                    {activeTab === 'calculator' && 'Herramientas de Nómina'}
                                    {activeTab === 'alerts' && 'Centro de Novedades'}
                                    {activeTab === 'claims' && 'Generador de Escritos'}
                                </h1>
                            </div>
                        </div>

                        {/* RIGHT: Profile & Actions */}
                        <div className="flex items-center gap-2 md:gap-4 shrink-0">
                            {/* Desktop Company Badge (Visible) */}
                            <div className="hidden md:block mr-4">
                                <CompanyBadge
                                    companyId={selectedCompanyId}
                                    showName={true}
                                />
                            </div>

                            <ProfileSwitcher />

                            <div className="hidden md:flex w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-500 p-[1px] shadow-lg shadow-cyan-500/20">
                                <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center">
                                    <User size={20} className="text-slate-400" />
                                </div>
                            </div>

                            {/* Mobile Hamburger (Far Right) */}
                            <button
                                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                                className="md:hidden p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] bg-[var(--card-bg)] border border-[var(--card-border)] rounded-lg"
                            >
                                {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
                            </button>
                        </div>
                    </header>

                    {/* MOBILE MENU DROPDOWN */}
                    <AnimatePresence>
                        {isMobileMenuOpen && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="md:hidden absolute top-16 left-0 right-0 bg-[var(--bg-primary)] border-b border-[var(--panel-border)] shadow-2xl z-20 overflow-hidden"
                            >
                                <div className="p-4 space-y-4">
                                    <div className="grid grid-cols-2 gap-3">
                                        {navItems.map(item => (
                                            <button
                                                key={item.id}
                                                onClick={() => {
                                                    setActiveTab(item.id);
                                                    setIsMobileMenuOpen(false);
                                                }}
                                                className={`flex flex-col items-center justify-center p-4 rounded-xl border transition-all gap-2 ${activeTab === item.id
                                                    ? 'bg-[var(--panel-bg)] border-cyan-500/50 text-[var(--text-primary)]'
                                                    : 'bg-[var(--card-bg)] border-[var(--card-border)] text-[var(--text-secondary)]'
                                                    }`}
                                            >
                                                <item.icon size={24} className={activeTab === item.id ? 'text-cyan-400' : ''} />
                                                <span className="text-xs font-medium">{item.label}</span>
                                            </button>
                                        ))}
                                    </div>

                                    <div className="h-px bg-[var(--panel-border)]"></div>

                                    <div className="flex items-center justify-between p-2">
                                        <div className="flex items-center gap-3">
                                            <span className="text-sm font-medium text-[var(--text-secondary)]">Modo Oscuro</span>
                                            <ThemeToggle />
                                        </div>
                                        <button
                                            onClick={() => {
                                                router.push('/dashboard/settings');
                                                setIsMobileMenuOpen(false);
                                            }}
                                            className="text-[var(--text-primary)] text-sm font-medium flex items-center gap-2 bg-[var(--panel-bg)]/50 px-3 py-1.5 rounded-lg border border-[var(--panel-border)]"
                                        >
                                            <Settings size={16} className="text-cyan-400" /> Configuración
                                        </button>
                                        <button onClick={handleLogout} className="text-red-400 text-sm font-medium flex items-center gap-2">
                                            <LogOut size={16} /> Salir
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Content Area */}
                    <div className="flex-1 overflow-hidden relative p-0 md:p-6 min-w-0">
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

            <PwaInstallGuide isOpen={showInstallGuide} onClose={() => setShowInstallGuide(false)} />

            {/* MobileNav Removed */}
        </div >
    );
}
