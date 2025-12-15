'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Loader2, Building2, Users, Award } from 'lucide-react';
import { SalaryService } from '@/lib/salary-service';

interface CascadingSelectorProps {
    onSelectionChange: (selection: { company: string; group: string; level: string }) => void;
    initialSelection?: { company: string; group: string; level: string };
    className?: string;
}

export default function CascadingSelector({ onSelectionChange, initialSelection, className }: CascadingSelectorProps) {
    const [companies, setCompanies] = useState<string[]>([]);
    const [groups, setGroups] = useState<string[]>([]);
    const [levels, setLevels] = useState<string[]>([]);

    const [selectedCompany, setSelectedCompany] = useState(initialSelection?.company || '');
    const [selectedGroup, setSelectedGroup] = useState(initialSelection?.group || '');
    const [selectedLevel, setSelectedLevel] = useState(initialSelection?.level || '');

    const [loadingCompanies, setLoadingCompanies] = useState(true);
    const [loadingGroups, setLoadingGroups] = useState(false);
    const [loadingLevels, setLoadingLevels] = useState(false);

    // Initial Load
    useEffect(() => {
        async function loadCompanies() {
            try {
                const data = await SalaryService.getCompanies();
                setCompanies(data);
                if (initialSelection?.company && data.includes(initialSelection.company)) {
                    setSelectedCompany(initialSelection.company);
                }
            } catch (err) {
                console.error("Failed to load companies", err);
            } finally {
                setLoadingCompanies(false);
            }
        }
        loadCompanies();
    }, [initialSelection]);

    // Load Groups when Company changes
    useEffect(() => {
        if (!selectedCompany) {
            setGroups([]);
            setSelectedGroup('');
            return;
        }

        async function loadGroups() {
            setLoadingGroups(true);
            try {
                const data = await SalaryService.getGroups(selectedCompany);
                setGroups(data);
                // Reset child selection if not matching initial
                if (initialSelection?.company === selectedCompany && initialSelection?.group) {
                    // Keep initial only if valid? assuming yes for now or logic elsewhere
                } else if (!data.includes(selectedGroup)) {
                    setSelectedGroup('');
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoadingGroups(false);
            }
        }
        loadGroups();
    }, [selectedCompany, initialSelection, selectedGroup]);
    // Dependency on selectedGroup logic above is tricky inside useEffect. 
    // Simpler: Just Fetch. Resetting logic handles itself.

    // Load Levels when Group changes
    useEffect(() => {
        if (!selectedCompany || !selectedGroup) {
            setLevels([]);
            setSelectedLevel('');
            return;
        }

        async function loadLevels() {
            setLoadingLevels(true);
            try {
                const data = await SalaryService.getLevels(selectedCompany, selectedGroup);
                setLevels(data);
                if (!data.includes(selectedLevel)) {
                    setSelectedLevel('');
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoadingLevels(false);
            }
        }
        loadLevels();
    }, [selectedCompany, selectedGroup, selectedLevel]);

    // Notify Parent
    useEffect(() => {
        onSelectionChange({
            company: selectedCompany,
            group: selectedGroup,
            level: selectedLevel
        });
    }, [selectedCompany, selectedGroup, selectedLevel, onSelectionChange]);


    const renderSelect = (
        label: string,
        icon: React.ReactNode,
        value: string,
        onChange: (val: string) => void,
        options: string[],
        loading: boolean,
        disabled: boolean
    ) => (
        <div className="relative mb-4">
            <label className="text-xs uppercase font-bold text-slate-500 mb-1 block pl-1">
                {label}
            </label>
            <div className="relative">
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
                    {loading ? <Loader2 className="animate-spin" size={18} /> : icon}
                </div>
                <select
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    disabled={disabled || loading}
                    className="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded-xl py-3 pl-10 pr-10 appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                    <option value="" disabled>Select {label}...</option>
                    {options.map(opt => (
                        <option key={opt} value={opt}>{opt}</option>
                    ))}
                </select>
                <div className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none">
                    <ChevronDown size={16} />
                </div>
            </div>
        </div>
    );

    return (
        <div className={className || "grid grid-cols-1 md:grid-cols-3 gap-4"}>
            {renderSelect(
                "Company",
                <Building2 size={18} />,
                selectedCompany,
                setSelectedCompany,
                companies,
                loadingCompanies,
                false
            )}

            {renderSelect(
                "Group",
                <Users size={18} />,
                selectedGroup,
                setSelectedGroup,
                groups,
                loadingGroups,
                !selectedCompany
            )}

            {renderSelect(
                "Level",
                <Award size={18} />,
                selectedLevel,
                setSelectedLevel,
                levels,
                loadingLevels,
                !selectedGroup
            )}
        </div>
    );
}
