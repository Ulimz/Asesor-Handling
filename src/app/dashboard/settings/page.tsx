'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiService, User } from '@/lib/api-service';
import { motion } from 'framer-motion';
import { Save, User as UserIcon, Trash2 } from 'lucide-react';

export default function SettingsPage() {
    const router = useRouter();
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState<Partial<User>>({});
    const [successMsg, setSuccessMsg] = useState('');

    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            router.push('/login');
            return;
        }
        apiService.getMe(token).then(u => {
            setUser(u);
            setFormData(u);
        }).catch(() => {
            router.push('/login');
        });
    }, [router]);

    const handleSave = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) return;
            const updated = await apiService.updateProfile(token, formData);
            setUser(updated);
            setSuccessMsg('Perfil actualizado correctamente');
            setTimeout(() => setSuccessMsg(''), 3000);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    if (!user) return <div className="p-8 text-white">Cargando...</div>;

    return (
        <div className="p-6 md:p-10 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-white mb-8 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <UserIcon className="text-cyan-400" /> Ajustes de Perfil
                </div>
                <button
                    onClick={() => window.location.href = '/dashboard'}
                    className="text-slate-400 hover:text-white transition-colors"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
            </h1>

            <div className="bg-slate-900/50 border border-white/5 rounded-2xl p-8 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-slate-400 mb-2">Nombre Preferido</label>
                        <input
                            value={formData.preferred_name || ''}
                            onChange={e => setFormData({ ...formData, preferred_name: e.target.value })}
                            className="w-full bg-slate-950 border border-white/10 rounded-lg p-3 text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-slate-400 mb-2">Grupo Laboral</label>
                        <select
                            className="w-full bg-slate-950 border border-white/10 rounded-lg p-3 text-white"
                            value={formData.job_group || ''}
                            onChange={(e) => setFormData({ ...formData, job_group: e.target.value })}
                        >
                            <option value="">Seleccionar...</option>
                            <option value="Administrativo">Administrativo</option>
                            <option value="Tecnico">Técnico/Gestor</option>
                            <option value="Auxiliar">Serv. Auxiliares</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-slate-400 mb-2">Nivel Salarial</label>
                        <input
                            type="number" min="1" max="25"
                            value={formData.salary_level || ''}
                            onChange={e => setFormData({ ...formData, salary_level: parseInt(e.target.value) })}
                            className="w-full bg-slate-950 border border-white/10 rounded-lg p-3 text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-slate-400 mb-2">Tipo Contrato</label>
                        <select
                            className="w-full bg-slate-950 border border-white/10 rounded-lg p-3 text-white"
                            value={formData.contract_type || ''}
                            onChange={(e) => setFormData({ ...formData, contract_type: e.target.value })}
                        >
                            <option value="Fijo">Fijo Tiempo Completo</option>
                            <option value="Fijo Parcial">Fijo Tiempo Parcial</option>
                            <option value="Fijo Discontinuo">Fijo Discontinuo</option>
                            <option value="Eventual">Eventual</option>
                        </select>
                    </div>
                </div>

                <div className="flex justify-end pt-6 border-t border-white/5">
                    <button
                        onClick={handleSave}
                        disabled={isLoading}
                        className="bg-cyan-600 text-white px-6 py-2 rounded-lg hover:bg-cyan-500 font-bold flex items-center gap-2"
                    >
                        <Save size={18} />
                        {isLoading ? 'Guardando...' : 'Guardar Cambios'}
                    </button>
                </div>
                {successMsg && <p className="text-green-400 text-right">{successMsg}</p>}
            </div>

            {/* Danger Zone */}
            <div className="mt-12 bg-red-900/10 border border-red-500/20 rounded-2xl p-8">
                <h2 className="text-xl font-bold text-red-500 mb-4 flex items-center gap-2">
                    <Trash2 size={24} /> Zona de Peligro
                </h2>
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <div>
                        <p className="text-slate-300 font-medium mb-1">Eliminar Cuenta</p>
                        <p className="text-sm text-slate-500">
                            Esta acción es permanente y no se puede deshacer. Todos tus datos serán borrados.
                        </p>
                    </div>
                    <button
                        onClick={async () => {
                            if (window.confirm('¿Estás SEGURO de que quieres eliminar tu cuenta? Esta acción no se puede deshacer.')) {
                                setIsLoading(true);
                                try {
                                    const token = localStorage.getItem('auth_token');
                                    if (token) {
                                        await apiService.deleteAccount(token);
                                        localStorage.removeItem('auth_token');
                                        window.location.href = '/';
                                    }
                                } catch (error) {
                                    console.error(error);
                                    alert("Error al eliminar cuenta");
                                } finally {
                                    setIsLoading(false);
                                }
                            }
                        }}
                        className="bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white border border-red-500/50 px-6 py-3 rounded-xl transition-all font-semibold text-sm whitespace-nowrap"
                    >
                        Eliminar definitivamente
                    </button>
                </div>
            </div>
        </div >
    );
}
