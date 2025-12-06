'use client';

import { motion } from 'framer-motion';
import { companies, CompanyId } from '@/data/knowledge-base';
import { ShieldCheck, ChevronRight } from 'lucide-react';

interface CompanySelectorProps {
    onSelect: (companyId: CompanyId) => void;
}

export default function CompanySelector({ onSelect }: CompanySelectorProps) {
    return (
        <div className="flex flex-col items-center justify-center min-h-[650px] w-full p-8">
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                className="text-center mb-16 relative z-10"
            >
                <div className="inline-flex items-center justify-center p-4 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-2xl mb-6 shadow-2xl border border-white/5 backdrop-blur-sm">
                    <ShieldCheck size={48} className="text-blue-400" strokeWidth={1.5} />
                </div>
                <h2 className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400 mb-6 tracking-tight">
                    Select Your Organization
                </h2>
                <p className="text-slate-400 text-lg max-w-xl mx-auto font-light leading-relaxed">
                    Access specialized legal intelligence tailored to your company's specific collective agreement.
                </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl px-4 z-10">
                {companies.map((company, idx) => (
                    <motion.button
                        key={company.id}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.1, duration: 0.4 }}
                        whileHover={{ scale: 1.02, y: -5 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => onSelect(company.id)}
                        className="group relative h-64 flex flex-col justify-between p-8 rounded-3xl bg-[#18181b] border border-white/5 hover:border-white/20 transition-all duration-300 overflow-hidden text-left"
                    >
                        {/* Dynamic Glow Gradient */}
                        <div
                            className="absolute -right-20 -top-20 w-40 h-40 rounded-full opacity-20 blur-3xl transition-opacity duration-300 group-hover:opacity-40"
                            style={{ backgroundColor: company.color }}
                        />

                        <div className="relative z-10">
                            <div
                                className="w-14 h-14 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg mb-6"
                                style={{
                                    background: `linear-gradient(135deg, ${company.color}, ${company.color}88)`
                                }}
                            >
                                {company.name.charAt(0)}
                            </div>
                            <h3 className="text-2xl font-semibold text-white mb-2 tracking-wide">
                                {company.name}
                            </h3>
                            <p className="text-sm text-slate-500 font-medium">
                                Collective Agreement Database
                            </p>
                        </div>

                        <div className="relative z-10 flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-slate-500 group-hover:text-white transition-colors">
                            <span>Initialize</span>
                            <ChevronRight size={14} />
                        </div>
                    </motion.button>
                ))}
            </div>

            {/* Background Atmosphere */}
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none -z-0"></div>
        </div>
    );
}
