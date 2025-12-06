'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { companies, CompanyId } from '@/data/knowledge-base';
import { ChevronDown, Check, Building2 } from 'lucide-react';

interface CompanyDropdownProps {
    selectedCompanyId: CompanyId | null;
    onSelect: (id: CompanyId) => void;
}

export default function CompanyDropdown({ selectedCompanyId, onSelect }: CompanyDropdownProps) {
    const [isOpen, setIsOpen] = useState(false);
    const selectedCompany = companies.find(c => c.id === selectedCompanyId);

    const toggleOpen = () => setIsOpen(!isOpen);

    return (
        <div className="relative w-full z-50">
            {/* Trigger Button */}
            <button
                onClick={toggleOpen}
                className="w-full flex items-center justify-between p-3 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all text-left"
            >
                <div className="flex items-center gap-3">
                    <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-sm"
                        style={{ backgroundColor: selectedCompany ? selectedCompany.color : '#64748b' }}
                    >
                        {selectedCompany ? selectedCompany.name.charAt(0) : <Building2 size={16} />}
                    </div>
                    <div>
                        <span className="block text-sm font-semibold text-slate-700">
                            {selectedCompany ? selectedCompany.name : 'Seleccionar Empresa'}
                        </span>
                        <span className="block text-[10px] text-slate-400 uppercase tracking-wide">
                            {selectedCompany ? 'Convenio Activo' : 'Requerido'}
                        </span>
                    </div>
                </div>
                <ChevronDown
                    size={16}
                    className={`text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
                />
            </button>

            {/* Dropdown Menu */}
            <AnimatePresence>
                {isOpen && (
                    <>
                        {/* Backdrop to close on click outside */}
                        <div
                            className="fixed inset-0 z-40"
                            onClick={() => setIsOpen(false)}
                        />

                        <motion.div
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 5 }}
                            className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-slate-100 overflow-hidden z-50"
                        >
                            <div className="p-1">
                                {companies.map((company) => (
                                    <button
                                        key={company.id}
                                        onClick={() => {
                                            onSelect(company.id);
                                            setIsOpen(false);
                                        }}
                                        className="w-full flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-50 transition-colors group relative"
                                    >
                                        <div
                                            className="w-6 h-6 rounded-md flex items-center justify-center text-white text-xs font-bold"
                                            style={{ backgroundColor: company.color }}
                                        >
                                            {company.name.charAt(0)}
                                        </div>
                                        <span className="flex-1 text-left text-sm font-medium text-slate-700 group-hover:text-slate-900">
                                            {company.name}
                                        </span>
                                        {selectedCompanyId === company.id && (
                                            <Check size={16} className="text-blue-500" />
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
