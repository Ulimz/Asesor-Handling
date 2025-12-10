'use client';

import { useState } from 'react';
import { Calculator, DollarSign, PieChart, ArrowRight } from 'lucide-react';
import { API_URL } from '@/config/api';

interface CalculationResult {
    gross_monthly: number;
    net_monthly: number;
    irpf_percentage: number;
    irpf_amount: number;
    social_security_amount: number;
    annual_net: number;
}

export default function SalaryCalculator() {
    const [grossSalary, setGrossSalary] = useState<number>(25000);
    const [payments, setPayments] = useState<number>(12);
    const [age, setAge] = useState<number>(30);
    const [result, setResult] = useState<CalculationResult | null>(null);
    const [loading, setLoading] = useState(false);

    const handleCalculate = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const res = await fetch(`${API_URL}/api/calculadoras/nomina`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    gross_annual_salary: grossSalary,
                    age: age,
                    payments: payments
                })
            });

            if (res.ok) {
                const data = await res.json();
                setResult(data);
            }
        } catch (error) {
            console.error("Error calculating salary", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl max-w-4xl mx-auto">
            <div className="flex items-center gap-3 mb-8">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
                    <Calculator size={24} />
                </div>
                <div>
                    <h2 className="text-2xl font-bold text-white">Calculadora de Nómina</h2>
                    <p className="text-slate-400 text-sm">Estima tu salario neto mensual según la normativa 2024</p>
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8">

                {/* INPUT FORM */}
                <form onSubmit={handleCalculate} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Salario Bruto Anual (€)</label>
                        <div className="relative">
                            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">€</span>
                            <input
                                type="number"
                                value={grossSalary}
                                onChange={(e) => setGrossSalary(Number(e.target.value))}
                                className="w-full bg-slate-800/50 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all font-mono"
                                placeholder="25000"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Pagas</label>
                            <select
                                value={payments}
                                onChange={(e) => setPayments(Number(e.target.value))}
                                className="w-full bg-slate-800/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500/50"
                            >
                                <option value={12}>12 Pagas</option>
                                <option value={14}>14 Pagas</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Edad</label>
                            <input
                                type="number"
                                value={age}
                                onChange={(e) => setAge(Number(e.target.value))}
                                className="w-full bg-slate-800/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500/50"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-4 bg-gradient-to-r from-emerald-500 to-green-600 rounded-xl font-bold text-white hover:shadow-lg hover:shadow-emerald-500/25 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        {loading ? 'Calculando...' : <>Calcular Neto <ArrowRight size={18} /></>}
                    </button>
                </form>

                {/* RESULTS PANEL */}
                <div className="bg-white/5 border border-white/5 rounded-2xl p-6 relative overflow-hidden">
                    {!result ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 text-center opacity-60">
                            <PieChart size={48} className="mb-4 text-slate-600" />
                            <p>Introduce tus datos para ver el desglose</p>
                        </div>
                    ) : (
                        <div className="space-y-6 relative z-10">
                            <div className="text-center pb-6 border-b border-white/5">
                                <p className="text-slate-400 text-sm mb-1">Salario Neto Mensual</p>
                                <div className="text-4xl font-bold text-emerald-400 font-mono">
                                    {result.net_monthly.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}
                                </div>
                                {payments === 14 && <span className="text-xs text-emerald-500/70 inline-block mt-2 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/10">14 Pagas</span>}
                            </div>

                            <div className="space-y-3">
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-400">Bruto Mensual</span>
                                    <span className="text-slate-200 font-medium">{result.gross_monthly.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-red-400">Retención IRPF ({result.irpf_percentage}%)</span>
                                    <span className="text-red-300 font-medium">-{result.irpf_amount.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}/año</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-orange-400">Seguridad Social</span>
                                    <span className="text-orange-300 font-medium">-{result.social_security_amount.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}/año</span>
                                </div>
                            </div>

                            <div className="pt-4 border-t border-white/5">
                                <div className="flex justify-between items-center bg-slate-800/50 p-3 rounded-lg border border-white/5">
                                    <span className="text-sm text-slate-300">Neto Anual</span>
                                    <span className="font-bold text-white font-mono">{result.annual_net.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}</span>
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
