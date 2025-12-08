'use client';

import { useState, useEffect } from 'react';
import { Bell, AlertTriangle, FileText, Shield, Info, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';

interface Alerta {
    id: number;
    title: string;
    description: string;
    type: 'convenio' | 'jurisprudencia' | 'seguridad' | 'reforma';
    created_at: string;
}

export default function AlertsPanel() {
    const [alertas, setAlertas] = useState<Alerta[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/alertas')
            .then(res => res.json())
            .then(data => {
                setAlertas(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching rules:", err);
                setLoading(false);
            });
    }, []);

    const getTypeIcon = (type: string) => {
        switch (type) {
            case 'convenio': return <FileText className="text-emerald-400" />;
            case 'jurisprudencia': return <Info className="text-blue-400" />;
            case 'seguridad': return <Shield className="text-red-400" />;
            case 'reforma': return <AlertTriangle className="text-amber-400" />;
            default: return <Bell className="text-slate-400" />;
        }
    };

    const getTypeColor = (type: string) => {
        switch (type) {
            case 'convenio': return 'border-emerald-500/30 bg-emerald-500/5';
            case 'jurisprudencia': return 'border-blue-500/30 bg-blue-500/5';
            case 'seguridad': return 'border-red-500/30 bg-red-500/5';
            case 'reforma': return 'border-amber-500/30 bg-amber-500/5';
            default: return 'border-slate-500/30 bg-slate-500/5';
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 pb-12">
            <header className="flex items-center gap-4 mb-8">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-white shadow-lg shadow-amber-500/20">
                    <Bell size={24} />
                </div>
                <div>
                    <h2 className="text-2xl font-bold text-white">Novedades y Alertas</h2>
                    <p className="text-slate-400 text-sm">Actualizaciones legislativas, cambios de convenio y avisos de seguridad.</p>
                </div>
            </header>

            {loading ? (
                <div className="flex justify-center p-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cyan-500"></div>
                </div>
            ) : (
                <div className="grid gap-4">
                    {alertas.map((alerta, i) => (
                        <motion.div
                            key={alerta.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className={`p-5 rounded-2xl border backdrop-blur-sm transition-all hover:bg-white/5 ${getTypeColor(alerta.type)}`}
                        >
                            <div className="flex items-start gap-4">
                                <div className="mt-1 p-2 rounded-lg bg-slate-900/50">
                                    {getTypeIcon(alerta.type)}
                                </div>
                                <div className="flex-1">
                                    <div className="flex justify-between items-start mb-1">
                                        <h3 className="font-semibold text-lg text-slate-200">{alerta.title}</h3>
                                        <span className="text-xs font-mono text-slate-500 flex items-center gap-1">
                                            <Calendar size={12} />
                                            {new Date(alerta.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <p className="text-slate-400 text-sm leading-relaxed">{alerta.description}</p>

                                    <div className="mt-3 flex gap-2">
                                        <span className="text-xs uppercase tracking-wider font-bold text-slate-500 bg-slate-900/50 px-2 py-1 rounded border border-white/5">
                                            {alerta.type}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}
