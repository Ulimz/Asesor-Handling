'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check, Building2, Loader2 } from 'lucide-react';
import { CompanyId } from '@/data/knowledge-base';
import { API_URL } from "@/config/api";

interface Company {
    id: number;
    slug: CompanyId;
    name: string;
    description: string;
    color: string;
    agreementLabel?: string;
}

interface CompanyDropdownProps {
    selectedCompanyId: CompanyId | null;
    onSelect: (id: CompanyId) => void;
}

export default function CompanyDropdown({ selectedCompanyId, onSelect }: CompanyDropdownProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [companies, setCompanies] = useState<Company[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchCompanies() {
            try {
                const res = await fetch(`${API_URL}/api/convenios/?t=${Date.now()}`);
                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
                }
                const data = await res.json();
                setCompanies(data);
                setError(null);
            } catch (error) {
                if (process.env.NODE_ENV !== 'production') {
                    console.error("Failed to load companies", error);
                }
                setError("No se pudieron cargar las empresas");
            } finally {
                setIsLoading(false);
            }
        }
        fetchCompanies();
    }, []);

    const selectedCompany = companies.find(c => c.slug === selectedCompanyId);

    const toggleOpen = () => setIsOpen(!isOpen);

    if (isLoading && companies.length === 0) {
        return (
            <div className="w-full h-14 bg-slate-800/50 rounded-xl animate-pulse flex items-center justify-center">
                <Loader2 className="animate-spin text-slate-500" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="w-full p-3 bg-red-900/20 border border-red-500/30 rounded-xl">
                <p className="text-xs text-red-400">{error}</p>
                <button
                    onClick={() => window.location.reload()}
                    className="text-xs text-red-300 underline mt-1"
                >
                    Recargar página
                </button>
            </div>
        );
    }

    return (
        <div className="relative w-full z-50">
            {/* Trigger Button */}
            <button
                onClick={toggleOpen}
                className="w-full flex items-center justify-between p-3 bg-slate-800/50 backdrop-blur-md border border-white/10 rounded-xl shadow-lg hover:border-cyan-500/50 hover:bg-slate-800/80 transition-all text-left group"
            >
                <div className="flex items-center gap-3">
                    <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-[0_0_10px_rgba(0,0,0,0.2)] border border-white/10"
                        style={{ backgroundColor: selectedCompany ? selectedCompany.color : '#334155' }}
                    >
                        {selectedCompany ? selectedCompany.name.charAt(0) : <Building2 size={16} />}
                    </div>
                    <div>
                        <span className="block text-sm font-semibold text-slate-200 group-hover:text-white transition-colors">
                            {selectedCompany ? selectedCompany.name : 'Seleccionar Empresa'}
                        </span>
                        <span className="block text-[10px] text-slate-400 uppercase tracking-wide">
                            {selectedCompany ? (selectedCompany.agreementLabel || 'Convenio Activo') : 'Requerido'}
                        </span>
                    </div>
                </div>
                <ChevronDown
                    size={16}
                    className={`text-slate-400 group-hover:text-cyan-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
                />
            </button>

            {/* Dropdown Menu */}
            <AnimatePresence>
                {isOpen && (
                    <>
                        {/* Backdrop to close on click outside */}
                        <div
                            className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm"
                            onClick={() => setIsOpen(false)}
                        />

                        <motion.div
                            initial={{ opacity: 0, y: 10, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 10, scale: 0.95 }}
                            className="absolute top-full left-0 right-0 mt-2 bg-slate-900/95 backdrop-blur-xl rounded-xl shadow-[0_10px_40px_-10px_rgba(0,0,0,0.5)] border border-white/10 overflow-hidden z-50 max-h-64 overflow-y-auto scrollbar-thin"
                        >
                            <div className="p-1.5 space-y-1">
                                {companies.map((company) => (
                                    <button
                                        key={company.id}
                                        onClick={() => {
                                            onSelect(company.slug);
                                            setIsOpen(false);
                                        }}
                                        className="w-full flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/5 hover:border-white/5 border border-transparent transition-all group relative"
                                    >
                                        <div
                                            className="w-6 h-6 rounded-md flex items-center justify-center text-white text-xs font-bold shadow-sm"
                                            style={{ backgroundColor: company.color }}
                                        >
                                            {company.name.charAt(0)}
                                        </div>
                                        <span className="flex-1 text-left text-sm font-medium text-slate-300 group-hover:text-white">
                                            {company.name}
                                        </span>
                                        {selectedCompanyId === company.slug && (
                                            <Check size={16} className="text-cyan-400 drop-shadow-[0_0_5px_rgba(34,211,238,0.5)]" />
                                        )}
                                    </button>
                                ))}
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
}
