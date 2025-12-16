'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ShieldCheck, User, Lock, Mail, ArrowRight, AlertCircle, Loader2, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_URL } from '@/config/api';
import CascadingSelector from '@/components/calculators/CascadingSelector';

export default function RegisterPage() {
    const router = useRouter();
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [companySlug, setCompanySlug] = useState('');
    const [preferredName, setPreferredName] = useState('');
    const [jobGroup, setJobGroup] = useState('');
    const [salaryLevel, setSalaryLevel] = useState('');
    const [contractType, setContractType] = useState('');

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        if (password !== confirmPassword) {
            setError("Las contraseñas no coinciden.");
            setIsLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_URL}/api/users/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    full_name: fullName,
                    password,
                    company_slug: companySlug,
                    preferred_name: preferredName || fullName.split(' ')[0], // Default 1st name
                    job_group: jobGroup,
                    salary_level: salaryLevel || null,
                    contract_type: contractType,
                    is_active: true
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Error al crear cuenta');
            }

            setSuccess(true);

            // Redirect to login after success
            setTimeout(() => {
                router.push('/login');
            }, 2000);

        } catch (err: any) {
            setError(err.message || 'Error desconocido.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 selection:bg-cyan-500/30 font-sans relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-900/20 via-slate-950 to-slate-950 -z-10"></div>

            {/* Animated Orbs */}
            <div className="absolute top-10 left-10 w-96 h-96 bg-cyan-500/5 rounded-full blur-[120px]"></div>
            <div className="absolute bottom-10 right-10 w-96 h-96 bg-purple-500/5 rounded-full blur-[120px]"></div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
                className="w-full max-w-md bg-slate-900/60 backdrop-blur-2xl border border-white/5 rounded-3xl p-8 shadow-2xl relative"
            >
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-2xl shadow-lg shadow-cyan-500/20 mb-4">
                        <User size={24} className="text-white" strokeWidth={2.5} />
                    </div>
                    <h1 className="text-2xl font-bold text-white mb-2">Crear Cuenta</h1>
                    <p className="text-slate-400 text-sm">Únete a la plataforma líder en handling</p>
                </div>

                {!success ? (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-4">
                            {/* Full Name */}
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <User size={18} className="text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                                </div>
                                <input
                                    type="text"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    className="w-full bg-slate-950/50 border border-white/10 rounded-xl py-3.5 pl-11 pr-4 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-medium text-sm"
                                    placeholder="Nombre Completo"
                                    required
                                />
                            </div>

                            {/* Email */}
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <Mail size={18} className="text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                                </div>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-slate-950/50 border border-white/10 rounded-xl py-3.5 pl-11 pr-4 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-medium text-sm"
                                    placeholder="Correo electrónico"
                                    required
                                />
                            </div>

                            {/* Password */}
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <Lock size={18} className="text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                                </div>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-slate-950/50 border border-white/10 rounded-xl py-3.5 pl-11 pr-4 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-medium text-sm"
                                    placeholder="Contraseña"
                                    minLength={6}
                                    required
                                />
                            </div>

                            {/* Confirm Password */}
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <ShieldCheck size={18} className="text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                                </div>
                                <input
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="w-full bg-slate-950/50 border border-white/10 rounded-xl py-3.5 pl-11 pr-4 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-medium text-sm"
                                    placeholder="Confirmar Contraseña"
                                    minLength={6}
                                    required
                                />
                            </div>

                            {/* Preferred Name (Ahora antes de Empresa) */}
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <User size={18} className="text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                                </div>
                                <input
                                    type="text"
                                    value={preferredName}
                                    onChange={(e) => setPreferredName(e.target.value)}
                                    className="w-full bg-slate-950/50 border border-white/10 rounded-xl py-3.5 pl-11 pr-4 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-medium text-sm"
                                    placeholder="¿Cómo quieres que te llame el asistente?"
                                />
                            </div>

                            {/* Dynamic Selector (Company -> Group -> Level) */}
                            <div className="bg-slate-900/40 p-3 rounded-xl border border-white/5">
                                <CascadingSelector
                                    onSelectionChange={(sel: { company: string; group: string; level: string }) => {
                                        setCompanySlug(sel.company);
                                        setJobGroup(sel.group);
                                        setSalaryLevel(sel.level);
                                    }}
                                />
                            </div>

                            {/* Contract Type */}
                            <div className="relative group">
                                <select
                                    value={contractType}
                                    onChange={(e) => setContractType(e.target.value)}
                                    className="w-full bg-slate-950/50 border border-white/10 rounded-xl py-3.5 px-4 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-medium text-sm appearance-none cursor-pointer"
                                >
                                    <option value="" className="bg-slate-900 text-slate-500">Tipo de Contrato</option>
                                    <option value="Fijo" className="bg-slate-900">Fijo Tiempo Completo</option>
                                    <option value="Fijo Parcial" className="bg-slate-900">Fijo Tiempo Parcial</option>
                                    <option value="Fijo Discontinuo" className="bg-slate-900">Fijo Discontinuo</option>
                                    <option value="Eventual" className="bg-slate-900">Eventual</option>
                                </select>
                            </div>
                        </div>

                        <AnimatePresence>
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="flex items-center gap-2 text-red-400 text-xs bg-red-500/10 p-3 rounded-lg border border-red-500/20"
                                >
                                    <AlertCircle size={14} />
                                    <span>{error}</span>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold py-3.5 rounded-xl transition-all shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none flex items-center justify-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 size={18} className="animate-spin" />
                                    <span>Registrando...</span>
                                </>
                            ) : (
                                <>
                                    <span>Crear Cuenta</span>
                                    <ArrowRight size={18} />
                                </>
                            )}
                        </button>
                    </form>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-center py-8 space-y-4"
                    >
                        <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                            <CheckCircle2 size={32} className="text-emerald-500" />
                        </div>
                        <h2 className="text-xl font-bold text-white">¡Cuenta Creada!</h2>
                        <p className="text-slate-400 text-sm">Te estamos redirigiendo al inicio de sesión...</p>
                    </motion.div>
                )}

                <div className="mt-8 text-center pt-6 border-t border-white/5">
                    <p className="text-slate-500 text-sm mb-2">¿Ya tienes cuenta?</p>
                    <Link href="/login" className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors text-sm">
                        Iniciar Sesión
                    </Link>
                </div>
            </motion.div>
        </div>
    );
}
