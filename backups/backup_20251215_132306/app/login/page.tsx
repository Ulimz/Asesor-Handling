'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { ShieldCheck, User, Lock, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_URL } from '@/config/api';
import BrandLogo from '@/components/BrandLogo';

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            // Using direct fetch to backend for now, later we can move to a service
            const response = await fetch(`${API_URL}/api/users/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'username': email,
                    'password': password,
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Error al iniciar sesión');
            }

            const data = await response.json();

            // Store token in localStorage
            localStorage.setItem('auth_token', data.access_token);

            // Allow time for storage to set before redirect
            setTimeout(() => {
                router.push('/dashboard');
            }, 500);

        } catch (err: any) {
            setError(err.message || 'Credenciales incorrectas. Inténtalo de nuevo.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center p-4 selection:bg-cyan-500/30 font-sans relative overflow-hidden transition-colors duration-300">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-900/20 via-[var(--bg-primary)] to-[var(--bg-primary)] -z-10 transition-colors duration-300"></div>
            <div className="absolute top-0 w-full h-px bg-gradient-to-r from-transparent via-[var(--panel-border)] to-transparent"></div>
            <div className="absolute bottom-0 w-full h-px bg-gradient-to-r from-transparent via-[var(--panel-border)] to-transparent"></div>

            {/* Animated Orbs */}
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-[100px] animate-pulse-slow"></div>
            <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-[100px] animate-pulse-slow delay-1000"></div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md bg-[var(--card-bg)] backdrop-blur-xl border border-[var(--card-border)] rounded-3xl p-8 shadow-2xl relative transition-colors duration-300"
            >
                {/* Glow Effect */}
                <div className="absolute -top-10 -right-10 w-20 h-20 bg-cyan-500/20 rounded-full blur-xl animate-pulse"></div>

                <div className="text-center mb-10">
                    <div className="flex justify-center mb-6">
                        <BrandLogo iconSize={80} textSize="2xl" />
                    </div>
                    <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">Bienvenido</h1>
                    <p className="text-[var(--text-secondary)] text-sm">Accede a tu asistente legal personal</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-4">
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                <User size={18} className="text-[var(--text-secondary)] group-focus-within:text-cyan-400 transition-colors" />
                            </div>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-[var(--panel-bg)]/50 border border-[var(--panel-border)] rounded-xl py-3.5 pl-11 pr-4 text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-medium"
                                placeholder="Correo electrónico"
                                required
                            />
                        </div>

                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                <Lock size={18} className="text-[var(--text-secondary)] group-focus-within:text-cyan-400 transition-colors" />
                            </div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-[var(--panel-bg)]/50 border border-[var(--panel-border)] rounded-xl py-3.5 pl-11 pr-4 text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-medium"
                                placeholder="Contraseña"
                                required
                            />
                        </div>
                    </div>

                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="flex items-center gap-2 text-red-500 dark:text-red-400 text-sm bg-red-100 dark:bg-red-500/10 p-3 rounded-lg border border-red-200 dark:border-red-500/20"
                            >
                                <AlertCircle size={16} />
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
                                <Loader2 size={20} className="animate-spin" />
                                <span>Accediendo...</span>
                            </>
                        ) : (
                            <>
                                <span>Iniciar Sesión</span>
                                <ArrowRight size={20} />
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-8 text-center pt-6 border-t border-[var(--panel-border)]">
                    <p className="text-[var(--text-secondary)] text-sm mb-2">¿No tienes cuenta?</p>
                    <Link href="/register" className="text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 dark:hover:text-cyan-300 font-medium transition-colors text-sm">
                        Crear una cuenta nueva
                    </Link>
                    <div className="mt-4">
                        <Link href="/" className="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
                            ← Volver al inicio
                        </Link>
                    </div>
                </div>
            </motion.div>
            <div className="absolute bottom-6 text-[var(--text-secondary)] text-xs font-mono">
                Development Build v0.1
            </div>
        </div>
    );
}
