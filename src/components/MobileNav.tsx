'use client';

import { MessageSquare, Calculator, PenTool, Bell } from 'lucide-react';
import { motion } from 'framer-motion';

interface MobileNavProps {
    activeTab: 'chat' | 'calculator' | 'alerts' | 'claims';
    setActiveTab: (tab: 'chat' | 'calculator' | 'alerts' | 'claims') => void;
}

export default function MobileNav({ activeTab, setActiveTab }: MobileNavProps) {
    const tabs = [
        { id: 'chat', icon: MessageSquare, label: 'Chat' },
        { id: 'calculator', icon: Calculator, label: 'Nómina' },
        { id: 'claims', icon: PenTool, label: 'Escritos' },
        { id: 'alerts', icon: Bell, label: 'Avisos' },
    ] as const;

    return (
        <div className="md:hidden fixed bottom-0 inset-x-0 z-50 p-4 pb-6 bg-gradient-to-t from-slate-950 via-slate-950/90 to-transparent pointer-events-none">
            <div className="bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl p-2 flex justify-between items-center pointer-events-auto max-w-sm mx-auto">
                {tabs.map((tab) => {
                    const isActive = activeTab === tab.id;
                    const Icon = tab.icon;

                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`relative flex flex-col items-center justify-center w-16 h-14 rounded-xl transition-all duration-300 ${isActive
                                    ? 'text-white'
                                    : 'text-slate-500 hover:text-slate-300'
                                }`}
                        >
                            {isActive && (
                                <motion.div
                                    layoutId="mobile-nav-active"
                                    className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-xl border border-white/10"
                                    initial={false}
                                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                                />
                            )}

                            <div className={`relative z-10 flex flex-col items-center gap-1 transition-transform duration-200 ${isActive ? '-translate-y-1' : ''}`}>
                                <Icon size={20} strokeWidth={isActive ? 2.5 : 2} className={isActive ? 'drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]' : ''} />
                                <span className={`text-[9px] font-medium tracking-wide ${isActive ? 'text-cyan-100' : ''}`}>
                                    {tab.label}
                                </span>
                            </div>

                            {isActive && (
                                <motion.div
                                    layoutId="mobile-nav-dot"
                                    className="absolute bottom-1.5 w-1 h-1 bg-cyan-400 rounded-full shadow-[0_0_8px_rgba(34,211,238,0.8)]"
                                    transition={{ duration: 0.2 }}
                                />
                            )}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
