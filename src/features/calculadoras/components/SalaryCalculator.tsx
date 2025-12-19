'use client';

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Calculator, DollarSign, PieChart, ArrowRight, User, Building2, Briefcase, Moon, Sun, Clock, Printer, RotateCcw } from 'lucide-react';
import { API_URL } from '@/config/api';
// import { apiService } from '@/lib/api-service'; // We use context now
import CascadingSelector from '@/components/calculators/CascadingSelector';
import { useProfile } from '@/context/ProfileContext';

interface CalculationResult {
    base_salary_monthly: number;
    variable_salary: number;
    gross_monthly_total: number;
    net_salary_monthly: number;
    breakdown: {
        name: string;
        amount: number;
        type: string;
    }[];
    annual_gross: number;
}

export default function SalaryCalculator() {
    const { activeProfile, updateProfile: updateActiveProfile, createProfile, loading: profileLoading } = useProfile();

    // Basic Inputs
    const [grossSalary, setGrossSalary] = useState<number>(0);
    const [payments, setPayments] = useState<number>(14);
    const [age, setAge] = useState<number>(30);
    const [contractPct, setContractPct] = useState<number>(100);
    const [contractType, setContractType] = useState<string>('indefinido');
    const [irpf, setIrpf] = useState<number>(15);

    // Smart Inputs (Profile)
    // Initialized from activeProfile if available, otherwise defaults
    const [company, setCompany] = useState<string>('iberia');
    const [group, setGroup] = useState<string>('Tecnicos');
    const [level, setLevel] = useState<string>('Nivel 1');
    const [hasProfile, setHasProfile] = useState(false);

    // Variable Inputs
    const [nightHours, setNightHours] = useState<number>(0);
    // ... (other states)

    const [result, setResult] = useState<CalculationResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Dynamic Concepts State
    const [concepts, setConcepts] = useState<any[]>([]);
    const [dynamicValues, setDynamicValues] = useState<Record<string, number>>({});

    // Reset handler
    const handleReset = () => {
        setDynamicValues({});
        setResult(null);
        setError(null);
    };

    // Helper to fetch concepts
    const loadConcepts = async (companySlug: string) => {
        const token = localStorage.getItem('auth_token');
        setConcepts([]);
        setDynamicValues({});
        try {
            const res = await fetch(`${API_URL}/api/calculadoras/concepts/${companySlug}`, {
                headers: { 'Authorization': `Bearer ${token || ''}` }
            });
            if (res.ok) {
                const data = await res.json();
                setConcepts(data);
            }
        } catch (err) {
            console.error("Failed to load concepts", err);
        }
    };

    const initialSyncRef = useRef(false);

    // Sync state with activeProfile once on load or when profile changes
    useEffect(() => {
        if (activeProfile && !initialSyncRef.current) {
            setCompany(activeProfile.company_slug);
            setGroup(activeProfile.job_group);
            setLevel(activeProfile.salary_level);
            setContractPct(activeProfile.contract_percentage || 100);
            setContractType(activeProfile.contract_type || 'indefinido');
            setHasProfile(true);
            initialSyncRef.current = true;
        } else if (!profileLoading && !initialSyncRef.current) {
            loadConcepts('iberia');
            initialSyncRef.current = true;
        }
    }, [activeProfile, profileLoading]);

    // Reset sync ref when the profile ID explicitly changes to allow switching profiles
    useEffect(() => {
        initialSyncRef.current = false;
    }, [activeProfile?.id]);

    // Load concepts whenever company changes (manual or profile-driven)
    useEffect(() => {
        if (company) {
            loadConcepts(company);
        }
    }, [company]);

    // Update prices dynamically when group or level changes
    useEffect(() => {
        if (concepts.length > 0 && group && level) {
            const updatedConcepts = concepts.map(c => {
                if (c.level_values && c.level_values[group] && c.level_values[group][level]) {
                    return { ...c, default_price: c.level_values[group][level] };
                }
                return c;
            });

            // If they actually changed, update state
            const hasChanged = JSON.stringify(updatedConcepts) !== JSON.stringify(concepts);
            if (hasChanged) {
                setConcepts(updatedConcepts);

                // Also update the base annual salary if SALARIO_BASE_ANUAL is present
                const baseConcept = updatedConcepts.find(c => c.code === 'SALARIO_BASE_ANUAL');
                if (baseConcept && baseConcept.default_price) {
                    setGrossSalary(baseConcept.default_price);
                }
            }
        }
    }, [group, level, concepts.length]); // concepts.length ensures we react when they initially load

    const handleCalculate = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null); // Clear previous errors

        const payload = {
            company_slug: company,
            user_group: group,
            user_level: level,
            contract_percentage: contractPct,
            contract_type: contractType,
            irpf_percentage: irpf,
            dynamic_variables: dynamicValues, // Send only dynamic map
            payments: payments,
            age: age,
            // If we have a company selected (Smart Mode), send 0 to force DB lookup.
            // Only send grossSalary if Manual Mode (no company or explicit manual override logic)
            gross_annual_salary: (company && company !== 'manual') ? 0 : grossSalary
        };

        console.log("Calculadora Payload:", payload);

        try {
            // Use Smart Calculator Endpoint
            const res = await fetch(`${API_URL}/api/calculadoras/smart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const data = await res.json();
                setResult(data);
            } else {
                const errText = await res.text();
                throw new Error(`Error ${res.status}: ${errText}`);
            }
        } catch (error: any) {
            console.error("Error calculating salary", error);
            setError(error.message || "Error desconocido al calcular");
        } finally {
            setLoading(false);
        }
    };

    // Memoize initialSelection to prevent cascading re-renders
    // Always pass current state to keep selector in sync
    const initialSelectionData = useMemo(() => {
        if (!activeProfile) return undefined;
        return {
            company: activeProfile.company_slug,
            group: activeProfile.job_group,
            level: activeProfile.salary_level
        };
    }, [activeProfile?.id]); // Only change when the profile ID changes

    // Memoize handler to prevent effect loops in child
    const handleSelectionChange = useCallback((sel: { company: string; group: string; level: string }) => {
        setCompany(sel.company);
        setGroup(sel.group);
        setLevel(sel.level);
    }, []);

    return (
        <div className="p-6 bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl max-w-5xl mx-auto">
            <div className="flex items-center gap-3 mb-8">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
                    <Calculator size={24} />
                </div>
                <div>
                    <h2 className="text-2xl font-bold text-white">Calculadora Inteligente (Dinámica)</h2>
                    <p className="text-slate-400 text-sm">
                        {activeProfile ? `Perfil: ${activeProfile.alias} (${company})` : 'Personaliza tu perfil y variables mensuales'}
                    </p>
                </div>
            </div>

            <div className="grid lg:grid-cols-12 gap-8">

                {/* INPUT FORM */}
                <form onSubmit={handleCalculate} className="lg:col-span-7 space-y-6">

                    {/* Sección Perfil */}
                    <div className="bg-slate-800/30 p-4 rounded-xl border border-white/5 space-y-4">
                        <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold uppercase tracking-wider mb-2">
                            <User size={16} /> Perfil Profesional
                        </div>

                        <CascadingSelector
                            initialSelection={initialSelectionData}
                            onSelectionChange={handleSelectionChange}
                        />
                    </div>

                    {/* Sección Jornada Laboral */}
                    <div className="bg-slate-800/30 p-4 rounded-xl border border-white/5 space-y-4">
                        <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold uppercase tracking-wider mb-2">
                            <Clock size={16} /> Jornada Laboral
                        </div>
                        <div className="space-y-2">
                            <div className="flex justify-between items-center text-sm text-slate-300">
                                <span>Porcentaje de Jornada</span>
                                <span className="font-mono text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">{contractPct}%</span>
                            </div>

                            {/* Manual Save Profile Button */}
                            {hasProfile && activeProfile && (
                                <div className="flex justify-end pt-2">
                                    <button
                                        type="button"
                                        onClick={async () => {
                                            if (company && group && level) {
                                                try {
                                                    await updateActiveProfile(activeProfile.id, {
                                                        company_slug: company,
                                                        job_group: group,
                                                        salary_level: level,
                                                        contract_percentage: contractPct,
                                                        contract_type: contractType
                                                    });
                                                    alert("Perfil actualizado correctamente");
                                                } catch (e) {
                                                    console.error("Save profile failed", e);
                                                    alert("Error al guardar perfil");
                                                }
                                            }
                                        }}
                                        className="text-xs flex items-center gap-1 text-emerald-400 hover:text-emerald-300 transition-colors"
                                    >
                                        <User size={14} /> Actualizar Perfil Activo ({activeProfile.alias})
                                    </button>
                                </div>
                            )}

                            {/* Save As New Button (Always visible if logged in?) - Simplified for now */}
                            {!activeProfile && (
                                <div className="flex justify-end pt-2">
                                    {/* Logic for creating first profile usually handled by registration or dashboard, but we can add 'Save as New' here later if needed */}
                                </div>
                            )}
                        </div>
                        <input
                            type="range"
                            min="10"
                            max="100"
                            step="1"
                            value={contractPct}
                            onChange={(e) => setContractPct(Number(e.target.value))}
                            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                        />
                        <p className="text-xs text-slate-500">
                            {contractPct === 100 ? 'Tiempo Completo (40h)' : `Tiempo Parcial (~${(40 * contractPct / 100).toFixed(1)}h semanales)`}
                        </p>
                    </div>

                    <div className="space-y-2 pt-2 border-t border-white/5">
                        <label className="text-xs text-slate-400 block mb-1">Tipo de Contrato</label>
                        <div className="flex bg-slate-900/50 rounded-lg p-1 border border-white/10">
                            <button
                                type="button"
                                onClick={() => setContractType('indefinido')}
                                className={`flex-1 py-2 text-xs font-medium rounded-md transition-all ${contractType === 'indefinido' ? 'bg-emerald-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                            >
                                Indefinido
                            </button>
                            <button
                                type="button"
                                onClick={() => setContractType('temporal')}
                                className={`flex-1 py-2 text-xs font-medium rounded-md transition-all ${contractType === 'temporal' ? 'bg-emerald-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                            >
                                Temporal
                            </button>
                        </div>
                    </div>

                    {/* Sección Impuestos (IRPF) */}
                    <div className="bg-slate-800/30 p-4 rounded-xl border border-white/5 space-y-4">
                        <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold uppercase tracking-wider mb-2">
                            <DollarSign size={16} /> Retenciones
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs text-slate-400 block mb-1">IRPF Voluntario (%)</label>
                                <div className="relative">
                                    <input
                                        type="number"
                                        value={irpf}
                                        onChange={e => setIrpf(Number(e.target.value))}
                                        className="w-full bg-slate-900/50 border border-white/10 rounded-lg py-2 pl-3 pr-8 text-sm text-white focus:border-emerald-500/50"
                                        step="0.1"
                                    />
                                    <span className="absolute right-3 top-2 text-slate-500 text-sm">%</span>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs text-slate-400 block mb-1">Seguridad Social</label>
                                <div className="w-full bg-slate-900/30 border border-white/5 rounded-lg py-2 px-3 text-sm text-slate-500 cursor-not-allowed">
                                    <div className="flex flex-col gap-1">
                                        <div className="flex justify-between">
                                            <span>Contingencias:</span>
                                            <span className="text-white">4.70%</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Desempleo:</span>
                                            <span className={contractType === 'temporal' ? 'text-amber-400 font-bold' : 'text-white'}>
                                                {contractType === 'temporal' ? '1.60%' : '1.55%'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>F.P.:</span>
                                            <span className="text-white">0.10%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Variables Mensuales DINÁMICAS */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold uppercase tracking-wider">
                            <Clock size={16} /> Variables Mensuales ({concepts.filter(c =>
                                !c.code.startsWith('PLUS_TURNOS') &&
                                !c.code.startsWith('PLUS_TURNICIDAD') &&
                                !c.code.startsWith('PLUS_FRACC') &&
                                !['PLUS_FIJI', 'PLUS_FTP', 'PLUS_SUPERV', 'PLUS_JEFE_SERV', 'PLUS_SUPERVISION', 'PLUS_JEFATURA', 'PLUS_JORNADA_IRREGULAR'].includes(c.code)
                            ).length})
                        </div>

                        {/* 1. GRUPO EXCLUYENTE: Régimen de Turnos / Jornada */}
                        {(concepts.some(c => c.code.startsWith('PLUS_TURNOS_')) || concepts.some(c => c.code.startsWith('PLUS_TURNICIDAD_')) || concepts.some(c => ['PLUS_FIJI', 'PLUS_FTP', 'PLUS_JORNADA_IRREGULAR'].includes(c.code))) && (
                            <div className="bg-slate-800/50 p-4 rounded-xl border border-white/5 space-y-2 mb-4">
                                <label className="text-sm font-medium text-slate-300 block">Régimen de Turnos / Jornada (Mutuamente Excluyentes)</label>
                                <select
                                    className="w-full bg-slate-900/50 border border-white/10 rounded-lg py-2 px-3 text-sm text-white focus:border-emerald-500/50"
                                    onChange={(e) => {
                                        const selection = e.target.value;
                                        const newValues = { ...dynamicValues };
                                        concepts.filter(c => c.code.startsWith('PLUS_TURNOS_') || c.code.startsWith('PLUS_TURNICIDAD_')).forEach(c => newValues[c.code] = 0);
                                        if (concepts.find(c => c.code === 'PLUS_FIJI')) newValues['PLUS_FIJI'] = 0;
                                        if (concepts.find(c => c.code === 'PLUS_FTP')) newValues['PLUS_FTP'] = 0;
                                        if (concepts.find(c => c.code === 'PLUS_JORNADA_IRREGULAR')) newValues['PLUS_JORNADA_IRREGULAR'] = 0;
                                        if (selection === 'PLUS_FIJI') newValues['PLUS_FIJI'] = 1;
                                        else if (selection === 'PLUS_FTP') newValues['PLUS_FTP'] = 1;
                                        else if (selection === 'PLUS_JORNADA_IRREGULAR') newValues['PLUS_JORNADA_IRREGULAR'] = 1;
                                        else if (selection.startsWith('PLUS_TURNOS_') || selection.startsWith('PLUS_TURNICIDAD_')) newValues[selection] = 1;
                                        setDynamicValues(newValues);
                                    }}
                                    defaultValue=""
                                >
                                    <option value="">-- Sin Plus de Régimen --</option>
                                    {concepts.filter(c => c.code.startsWith('PLUS_TURNOS_') || c.code.startsWith('PLUS_TURNICIDAD_')).sort((a, b) => a.code.localeCompare(b.code)).map(c => (
                                        <option key={c.code} value={c.code}>
                                            {c.name.replace('Plus Turnicidad', 'Turnicidad').replace('Turnicidad', 'Turnicidad').trim()} ({c.default_price > 0 ? c.default_price.toFixed(2) + '€' : 'Variable'})
                                        </option>
                                    ))}
                                    {(concepts.find(c => c.code === 'PLUS_FIJI') || concepts.find(c => c.code === 'PLUS_JORNADA_IRREGULAR')) &&
                                        <option value={concepts.find(c => c.code === 'PLUS_JORNADA_IRREGULAR') ? 'PLUS_JORNADA_IRREGULAR' : 'PLUS_FIJI'}>
                                            Jornada Irregular / Fiji
                                        </option>
                                    }
                                    {concepts.find(c => c.code === 'PLUS_FTP') && <option value="PLUS_FTP">Fijo Tiempo Parcial (FTP)</option>}
                                </select>
                                <p className="text-xs text-slate-500">Selecciona tu régimen. Fiji, FTP y Turnicidad son incompatibles entre sí.</p>
                            </div>
                        )}

                        {/* 2. GRUPO FIJO: Pluses de Responsabilidad / Fijos */}
                        {concepts.some(c => ['PLUS_SUPERV', 'PLUS_JEFE_SERV', 'PLUS_PRODUCT', 'PLUS_MULTITASK', 'PLUS_RCO', 'PLUS_ARCO', 'PLUS_SUPERVISION', 'PLUS_JEFATURA'].includes(c.code)) && (
                            <div className="bg-slate-800/50 p-4 rounded-xl border border-white/5 space-y-2 mb-4">
                                <label className="text-sm font-medium text-slate-300 block">Pluses Fijos / Responsabilidad</label>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    {concepts.filter(c => ['PLUS_SUPERV', 'PLUS_JEFE_SERV', 'PLUS_PRODUCT', 'PLUS_MULTITASK', 'PLUS_RCO', 'PLUS_ARCO', 'PLUS_SUPERVISION', 'PLUS_JEFATURA'].includes(c.code)).map(c => (
                                        <label key={c.code} className="flex items-center gap-2 p-2 rounded-lg bg-slate-900/40 border border-white/5 cursor-pointer hover:bg-slate-900/60 transition-colors">
                                            <input
                                                type="checkbox"
                                                className="w-4 h-4 rounded border-slate-600 text-emerald-500 focus:ring-emerald-500/50 bg-slate-800"
                                                checked={dynamicValues[c.code] === 1}
                                                onChange={(e) => {
                                                    setDynamicValues(prev => ({
                                                        ...prev,
                                                        [c.code]: e.target.checked ? 1 : 0
                                                    }));
                                                }}
                                            />
                                            <span className="text-sm text-slate-300 select-none">
                                                {c.name.replace('Plus ', '').replace('de ', '')}
                                                {c.default_price > 0 && <span className="text-emerald-500/80 text-xs ml-1">({c.default_price.toFixed(2)}€)</span>}
                                            </span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Special Group: Plus Jornada Fraccionada */}
                        {concepts.some(c => c.code.startsWith('PLUS_FRACC')) && (
                            <div className="bg-slate-800/50 p-4 rounded-xl border border-white/5 space-y-3 mb-4">
                                <label className="text-sm font-medium text-slate-300 block">Plus Jornada Fraccionada (Desglose)</label>
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                    {concepts.filter(c => c.code.startsWith('PLUS_FRACC')).map(fracc => (
                                        <div key={fracc.code} className="bg-slate-900/40 p-2 rounded-lg border border-white/5">
                                            <label className="text-xs text-slate-400 block mb-1 min-h-[32px]">{fracc.name.replace('Plus Fraccionada', '').replace('(', '').replace(')', '').trim() || fracc.name}</label>
                                            <div className="relative">
                                                <input
                                                    type="number"
                                                    placeholder="Días"
                                                    value={dynamicValues[fracc.code] || ''}
                                                    onChange={(e) => setDynamicValues(prev => ({
                                                        ...prev,
                                                        [fracc.code]: Number(e.target.value)
                                                    }))}
                                                    className="w-full bg-slate-900/50 border border-white/10 rounded-lg py-2 px-3 text-sm text-white focus:border-emerald-500/50"
                                                />
                                                <div className="text-[10px] text-emerald-500/80 mt-1 text-right">{fracc.default_price.toFixed(2)}€/día</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <p className="text-xs text-slate-500">Introduce los días realizados en cada tramo de fraccionada.</p>
                            </div>
                        )}

                        {concepts.length === 0 ? (
                            <div className="text-slate-500 text-sm italic">Cargando conceptos del convenio...</div>
                        ) : (
                            <div className="grid grid-cols-2 gap-4">
                                {concepts.filter(c =>
                                    !c.code.startsWith('PLUS_TURNOS') &&
                                    !c.code.startsWith('PLUS_TURNICIDAD') &&
                                    !c.code.startsWith('PLUS_FRACC') &&
                                    !['PLUS_FIJI', 'PLUS_FTP', 'PLUS_SUPERV', 'PLUS_JEFE_SERV', 'PLUS_PRODUCT', 'PLUS_MULTITASK', 'PLUS_RCO', 'PLUS_ARCO', 'PLUS_SUPERVISION', 'PLUS_JEFATURA', 'PLUS_JORNADA_IRREGULAR', 'SALARIO_BASE_ANUAL', 'SALARIO_BASE'].includes(c.code)
                                ).map((concept) => (
                                    <div key={concept.code} className="space-y-2">
                                        <label className="text-xs text-slate-300 flex items-center gap-2 truncate" title={concept.description}>
                                            {concept.name}
                                        </label>
                                        <input
                                            type="number"
                                            value={dynamicValues[concept.code] || ''}
                                            onChange={(e) => setDynamicValues(prev => ({
                                                ...prev,
                                                [concept.code]: Number(e.target.value)
                                            }))}
                                            className="w-full bg-slate-800/50 border border-white/10 rounded-xl py-2 px-3 text-white focus:outline-none focus:border-emerald-500/50 text-sm"
                                            placeholder="0"
                                        />
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="space-y-2 pt-4 border-t border-white/5">
                            <label className="text-sm font-medium text-slate-300">Pagas</label>
                            <select
                                value={payments}
                                onChange={(e) => setPayments(Number(e.target.value))}
                                className="w-full bg-slate-800/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500/50"
                            >
                                <option value={14}>14 Pagas</option>
                                <option value={12}>12 Pagas</option>
                            </select>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-4 bg-gradient-to-r from-emerald-500 to-green-600 rounded-xl font-bold text-white hover:shadow-lg hover:shadow-emerald-500/25 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        {loading ? 'Calculando...' : <>Calcular Nómina Inteligente <ArrowRight size={18} /></>}
                    </button>
                </form>

                {/* RESULTS PANEL */}
                <div id="results-panel" className="lg:col-span-5 bg-white/5 border border-white/5 rounded-2xl p-6 relative overflow-hidden flex flex-col">

                    {/* Buttons: Reset & Print */}
                    <div className="absolute top-4 right-4 flex gap-2 z-20 no-print">
                        {result && (
                            <button
                                onClick={handleReset}
                                className="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                                title="Nueva Nómina (Limpiar)"
                            >
                                <RotateCcw size={20} />
                            </button>
                        )}
                        <button
                            onClick={() => window.print()}
                            className="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                            title="Imprimir / Guardar PDF"
                        >
                            <Printer size={20} />
                        </button>
                    </div>

                    {error && (
                        <div className="bg-red-500/10 border border-red-500/20 text-red-200 text-sm p-3 rounded-lg mb-4">
                            <strong>Ha ocurrido un error:</strong> {typeof error === 'object' ? JSON.stringify(error) : error}
                        </div>
                    )}

                    {!result ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 text-center opacity-60 min-h-[300px]">
                            <PieChart size={48} className="mb-4 text-slate-600" />
                            <p>Introduce tus variables para ver el desglose detallado</p>
                        </div>
                    ) : (
                        <div className="space-y-6 relative z-10 flex-1">
                            <div className="text-center pb-6 border-b border-white/5">
                                <p className="text-slate-400 text-sm mb-1 uppercase tracking-widest">Neto Estimado</p>
                                <div className="text-5xl font-bold text-emerald-400 font-mono tracking-tight">
                                    {result?.net_salary_monthly?.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}
                                </div>
                                <div className="mt-2 text-xs text-slate-500">
                                    Bruto: {result?.gross_monthly_total.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}
                                </div>
                            </div>

                            <div className="space-y-3 flex-1 overflow-y-auto max-h-[400px] pr-2 custom-scrollbar print:max-h-none print:overflow-visible">
                                <h4 className="text-xs font-semibold text-slate-500 uppercase">Desglose de Conceptos</h4>
                                {result?.breakdown.map((item, idx) => (
                                    <div key={idx} className="flex justify-between text-sm group hover:bg-white/5 p-1 rounded transition-colors">
                                        <span className={item.type === 'deduccion' ? "text-red-400" : "text-slate-300"}>
                                            {item.name}
                                        </span>
                                        <span className={item.type === 'deduccion' ? "text-red-400 font-mono" : "text-emerald-400 font-mono"}>
                                            {item.amount.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}
                                        </span>
                                    </div>
                                ))}
                            </div>

                            <div className="pt-4 mt-auto border-t border-white/5">
                                <div className="flex justify-between items-center text-xs text-slate-500 mb-4">
                                    <span>Variables Totales</span>
                                    <span className="text-white">{result?.variable_salary.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}</span>
                                </div>

                                {/* Legal Disclaimer */}
                                <div className="bg-slate-800/50 p-3 rounded-lg border border-white/5 text-[10px] text-slate-300 leading-tight text-justify print:bg-white print:text-black print:border-black/10 print:mt-8">
                                    <strong>AVISO LEGAL:</strong> Este cálculo es una estimación meramente informativa y <u>no tiene carácter vinculante</u> ni validez legal. Los importes pueden variar debido a redondeos, cambios normativos o situaciones personales específicas no contempladas. Recomendamos contrastar estos datos con su nómina oficial o consultar con el departamento de RRHH.
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Background Glow */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-emerald-500/10 rounded-full blur-[60px] -z-10 pointer-events-none"></div>
                </div>
            </div>
        </div>
    );
}
