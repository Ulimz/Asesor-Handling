'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Loader2, Building2, Users, Award } from 'lucide-react';
import { SalaryService } from '@/lib/salary-service';

interface CascadingSelectorProps {
    onSelectionChange: (selection: { company: string; group: string; level: string }) => void;
    initialSelection?: { company: string; group: string; level: string };
}

export default function CascadingSelector({ onSelectionChange, initialSelection }: CascadingSelectorProps) {
    const [companies, setCompanies] = useState<string[]>([]);
    const [groups, setGroups] = useState<string[]>([]);
    const [levels, setLevels] = useState<string[]>([]);

    const [selectedCompany, setSelectedCompany] = useState(initialSelection?.company || '');
    const [selectedGroup, setSelectedGroup] = useState(initialSelection?.group || '');
    const [selectedLevel, setSelectedLevel] = useState(initialSelection?.level || '');

    const [loadingCompanies, setLoadingCompanies] = useState(true);
    const [loadingGroups, setLoadingGroups] = useState(false);
    const [loadingLevels, setLoadingLevels] = useState(false);

    // Initial Load & Sync with Props
    useEffect(() => {
        let mounted = true;

        async function loadCompanies() {
            try {
                const data = await SalaryService.getCompanies();
                if (mounted) {
                    setCompanies(data);
                }
            } catch (err) {
                console.error("CascadingSelector: Failed to load companies", err);
                if (mounted) setCompanies([]);
            } finally {
                if (mounted) setLoadingCompanies(false);
            }
        }

        // Only load companies if not loaded yet
        if (companies.length === 0) {
            loadCompanies();
        }

        return () => { mounted = false; };
    }, []); // Only run once on mount

    // Sync with initialSelection prop changes
    useEffect(() => {
        if (initialSelection) {
            if (initialSelection.company !== selectedCompany) {
                setSelectedCompany(initialSelection.company);
            }
            if (initialSelection.group !== selectedGroup) {
                setSelectedGroup(initialSelection.group);
            }
            if (initialSelection.level !== selectedLevel) {
                setSelectedLevel(initialSelection.level);
            }
        }
    }, [initialSelection]); // React to prop changes

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

                // Only reset if current selection is invalid AND we are not trying to set the initial selection
                // This logic needs to be careful. 
                // If initialSelection aligns with this company, we trust the first effect to set selectedGroup.
                // We just check validity here.
                if (!data.includes(selectedGroup) && selectedGroup !== '') {
                    // Wait, if selectedGroup comes from initialSelection, it might be set BEFORE groups are loaded.
                    // The first effect sets selectedGroup. 
                    // This effect loads groups. 
                    // If data doesn't include it (e.g. data mismatch), clear it.
                    // But we must NOT exclude the case where it IS valid.

                    // Optimization: Check against initialSelection to avoid clearing pending sync?
                    // Actually, if data is loaded and selectedGroup is not in it, it's invalid regardless of source.
                    // Exception: if initially loading.

                    // If data.includes(selectedGroup) is false, we clear it.
                    if (initialSelection?.group === selectedGroup && initialSelection?.company === selectedCompany) {
                        // It matches initial, maybe we keep it? 
                        // But if the API says it's invalid, we probably should clear it or let it be but it won't be in dropdown.
                        // Let's err on side of validity.
                        const isValid = data.includes(selectedGroup);
                        if (!isValid) setSelectedGroup('');
                    } else {
                        setSelectedGroup('');
                    }
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoadingGroups(false);
            }
        }
        loadGroups();
    }, [selectedCompany]); // Removed initialSelection and selectedGroup to prevent loops

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

                if (!data.includes(selectedLevel) && selectedLevel !== '') {
                    // Same validity check logic
                    if (initialSelection?.level === selectedLevel && initialSelection?.group === selectedGroup) {
                        const isValid = data.includes(selectedLevel);
                        if (!isValid) setSelectedLevel('');
                    } else {
                        setSelectedLevel('');
                    }
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoadingLevels(false);
            }
        }
        loadLevels();
    }, [selectedCompany, selectedGroup]); // Removed selectedLevel to prevent loops

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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
