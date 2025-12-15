'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, Briefcase, Calendar, ChevronRight, Check } from 'lucide-react';
import { apiService, User } from '@/lib/api-service';

export default function OnboardingPage() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [companies, setCompanies] = useState<any[]>([]);
    const [formData, setFormData] = useState({
        preferred_name: '',
        company_slug: '',
        job_group: '',
        salary_level: '',
        contract_type: 'Fijo',
        seniority_date: new Date().toISOString().split('T')[0]
    });

    const [error, setError] = useState('');

    useEffect(() => {
        // Load companies
        apiService.getCompanies()
            .then(data => {
                console.log('Companies loaded:', data);
                if (Array.isArray(data) && data.length > 0) {
                    setCompanies(data);
                } else {
                    setError('No se encontraron empresas disponibles.');
                }
            })
            .catch(err => {
                console.error('Error loading companies:', err);
                setError('Error de conexión: ' + err.message);
            });
    }, []);

    const handleNext = () => setStep(step + 1);

    const handleSubmit = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) return router.push('/login');

            await apiService.updateProfile(token, formData);
            router.push('/dashboard');
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 font-sans text-slate-200">
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-2xl bg-slate-900/80 border border-white/10 rounded-2xl p-8 shadow-2xl"
            >
                {/* Progress Bar */}
                <div className="flex gap-2 mb-8">
                    {[1, 2, 3].map(i => (
                        <div key={i} className={`h-1 flex-1 rounded-full transition-colors ${i <= step ? 'bg-cyan-500' : 'bg-slate-800'}`} />
                    ))}
                </div>

                <AnimatePresence mode="wait">
                    {step === 1 && (
                        <motion.div key="step1" initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -20, opacity: 0 }}>
                            <h2 className="text-2xl font-bold text-white mb-2">Vamos a conocerte</h2>
                            <p className="text-slate-400 mb-6">¿Cómo te gustaría que te llamemos?</p>

                            <label className="block text-sm font-medium mb-2 text-slate-300">Nombre Preferido</label>
                            <input
                                type="text"
                                value={formData.preferred_name}
                                onChange={(e) => setFormData({ ...formData, preferred_name: e.target.value })}
                                className="w-full bg-slate-950 border border-white/10 rounded-lg p-3 focus:border-cyan-500 outline-none"
                                placeholder="Ej: Uli"
                            />

                            <div className="mt-8 flex justify-end">
                                <button onClick={handleNext} disabled={!formData.preferred_name} className="bg-cyan-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-cyan-500 disabled:opacity-50">
                                    Continuar <ChevronRight className="inline w-4 h-4 ml-1" />
                                </button>
                            </div>
                        </motion.div>
                    )}

                    {step === 2 && (
                        <motion.div key="step2" initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -20, opacity: 0 }}>
                            <h2 className="text-2xl font-bold text-white mb-2">Tu Empresa</h2>
                            <p className="text-slate-400 mb-6">Selecciona dónde trabajas para cargar tu convenio.</p>

                            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                {error && (
                                    <div className="col-span-full p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-center">
                                        <p>{error}</p>
                                        <button
                                            onClick={() => window.location.reload()}
                                            className="mt-2 text-sm underline hover:text-red-300"
                                        >
                                            Reintentar
                                        </button>
                                    </div>
                                )}

                                {companies.map((c) => (
                                    <div
                                        key={c.id}
                                        onClick={() => setFormData({ ...formData, company_slug: c.slug })}
                                        className={`p-4 border rounded-xl cursor-pointer transition-all ${formData.company_slug === c.slug
                                            ? 'border-cyan-500 bg-cyan-500/10 text-white'
                                            : 'border-white/10 hover:border-white/20 hover:bg-white/5'
                                            }`}
                                    >
                                        <Building2 className="w-6 h-6 mb-2 text-cyan-400" />
                                        <div className="font-medium text-sm">{c.name}</div>
                                    </div>
                                ))}
                            </div>

                            <div className="mt-8 flex justify-end">
                                <button onClick={handleNext} disabled={!formData.company_slug} className="bg-cyan-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-cyan-500 disabled:opacity-50">
                                    Continuar <ChevronRight className="inline w-4 h-4 ml-1" />
                                </button>
                            </div>
                        </motion.div>
                    )}

                    {step === 3 && (
                        <motion.div key="step3" initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -20, opacity: 0 }}>
                            <h2 className="text-2xl font-bold text-white mb-2">Datos Profesionales</h2>
                            <p className="text-slate-400 mb-6">Esto nos ayuda a calcular tus nóminas y pluses.</p>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2 text-slate-300">Grupo Laboral</label>
                                    <select
                                        className="w-full bg-slate-950 border border-white/10 rounded-lg p-3 focus:border-cyan-500 outline-none"
                                        value={formData.job_group}
                                        onChange={(e) => setFormData({ ...formData, job_group: e.target.value })}
                                    >
                                        <option value="">Seleccionar...</option>
                                        <option value="Administrativo">Administrativo</option>
                                        <option value="Tecnico">Técnico/Gestor</option>
                                        <option value="Auxiliar">Serv. Auxiliares</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2 text-slate-300">Nivel Salarial</label>
                                    <input
                                        type="text"
                                        value={formData.salary_level}
                                        onChange={(e) => setFormData({ ...formData, salary_level: e.target.value })}
                                        className="w-full bg-slate-950 border border-white/10 rounded-lg p-3 focus:border-cyan-500 outline-none"
                                        placeholder="Ej: Nivel 1, Entrada..."
                                    />
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium mb-2 text-slate-300">Tipo Contrato</label>
                                    <select
                                        className="w-full bg-slate-950 border border-white/10 rounded-lg p-3 focus:border-cyan-500 outline-none"
                                        value={formData.contract_type}
                                        onChange={(e) => setFormData({ ...formData, contract_type: e.target.value })}
                                    >
                                        <option value="Fijo">Fijo Tiempo Completo</option>
                                        <option value="Fijo Parcial">Fijo Tiempo Parcial</option>
                                        <option value="Fijo Discontinuo">Fijo Discontinuo</option>
                                        <option value="Eventual">Eventual</option>
                                    </select>
                                </div>
                            </div>

                            <div className="mt-8 flex justify-end">
                                <button onClick={handleSubmit} disabled={isLoading} className="bg-gradient-to-r from-emerald-500 to-green-600 text-white px-8 py-2 rounded-lg font-bold hover:shadow-lg hover:shadow-emerald-500/20 transition-all flex items-center">
                                    {isLoading ? 'Guardando...' : 'Finalizar'} <Check className="inline w-4 h-4 ml-2" />
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div>
    );
}
