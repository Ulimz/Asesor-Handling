'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, Users, Database, ArrowLeft, Search, CheckCircle, XCircle } from 'lucide-react';
import { API_URL } from '@/config/api';

interface AdminStats {
    total_users: number;
    total_profiles: number;
    active_users: number;
}

interface AdminUser {
    id: number;
    email: string;
    full_name: string;
    is_active: boolean;
    is_superuser: boolean;
    created_at_approx: string | null;
}

export default function AdminPage() {
    const router = useRouter();
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [users, setUsers] = useState<AdminUser[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('auth_token');

                // 1. Fetch Stats
                const resStats = await fetch(`${API_URL}/api/admin/stats`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (resStats.status === 403) {
                    setError("Acceso Denegado: No tienes privilegios de Administrador.");
                    setLoading(false);
                    return;
                }

                if (resStats.ok) {
                    setStats(await resStats.json());
                }

                // 2. Fetch Users
                const resUsers = await fetch(`${API_URL}/api/admin/users`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (resUsers.ok) {
                    setUsers(await resUsers.json());
                }

            } catch (err) {
                console.error("Admin Load Error", err);
                setError("Error de conexión con el servidor.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const filteredUsers = users.filter(u =>
        u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        u.full_name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (error) {
        return (
            <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
                <Shield size={64} className="text-red-500 mb-4" />
                <h1 className="text-2xl font-bold text-white mb-2">Acceso Restringido</h1>
                <p className="text-red-400 mb-6">{error}</p>
                <button
                    onClick={() => router.push('/dashboard')}
                    className="px-6 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors"
                >
                    Volver al Dashboard
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200">
            {/* Header */}
            <div className="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 md:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => router.push('/dashboard')}
                            className="p-2 hover:bg-white/5 rounded-full text-slate-400 hover:text-white transition-colors"
                        >
                            <ArrowLeft size={20} />
                        </button>
                        <h1 className="text-xl font-bold text-white flex items-center gap-2">
                            <Shield className="text-amber-500" size={24} />
                            Panel de Administración
                        </h1>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 md:px-8 py-8 space-y-8">

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 flex items-center gap-4">
                        <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400">
                            <Users size={24} />
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm uppercase">Total Usuarios</p>
                            <p className="text-3xl font-bold text-white">{loading ? '...' : stats?.total_users}</p>
                        </div>
                    </div>

                    <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 flex items-center gap-4">
                        <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400">
                            <CheckCircle size={24} />
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm uppercase">Usuarios Activos</p>
                            <p className="text-3xl font-bold text-white">{loading ? '...' : stats?.active_users}</p>
                        </div>
                    </div>

                    <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 flex items-center gap-4">
                        <div className="p-3 bg-purple-500/10 rounded-lg text-purple-400">
                            <Database size={24} />
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm uppercase">Perfiles Profesionales</p>
                            <p className="text-3xl font-bold text-white">{loading ? '...' : stats?.total_profiles}</p>
                        </div>
                    </div>
                </div>

                {/* Search & Table */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-white">Usuarios del Sistema</h2>
                        <div className="relative">
                            <Search className="absolute left-3 top-2.5 text-slate-500" size={16} />
                            <input
                                type="text"
                                placeholder="Buscar usuario..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-white focus:border-amber-500/50 outline-none w-64"
                            />
                        </div>
                    </div>

                    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                                <tr>
                                    <th className="p-4 font-medium">ID</th>
                                    <th className="p-4 font-medium">Usuario</th>
                                    <th className="p-4 font-medium">Email</th>
                                    <th className="p-4 font-medium text-center">Admin</th>
                                    <th className="p-4 font-medium text-center">Estado</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {loading ? (
                                    <tr>
                                        <td colSpan={5} className="p-8 text-center text-slate-500">Cargando datos...</td>
                                    </tr>
                                ) : filteredUsers.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="p-8 text-center text-slate-500">No se encontraron usuarios.</td>
                                    </tr>
                                ) : (
                                    filteredUsers.map(user => (
                                        <tr key={user.id} className="hover:bg-slate-800/50 transition-colors">
                                            <td className="p-4 text-slate-500">#{user.id}</td>
                                            <td className="p-4 font-medium text-white">{user.full_name}</td>
                                            <td className="p-4 text-slate-400">{user.email}</td>
                                            <td className="p-4 text-center">
                                                {user.is_superuser ?
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-500/10 text-amber-500 border border-amber-500/20">ADMIN</span>
                                                    : <span className="text-slate-600">-</span>
                                                }
                                            </td>
                                            <td className="p-4 text-center">
                                                {user.is_active ?
                                                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-emerald-500/10 text-emerald-500">
                                                        <CheckCircle size={14} />
                                                    </span>
                                                    :
                                                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-red-500/10 text-red-500">
                                                        <XCircle size={14} />
                                                    </span>
                                                }
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    );
}
