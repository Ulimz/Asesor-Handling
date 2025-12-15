'use client';

import { useState } from 'react';
import { PenTool, FileText, Download, Copy, Check } from 'lucide-react';
import { API_URL } from '@/config/api';

export default function ClaimGenerator() {
    const [type, setType] = useState('vacaciones');
    const [userName, setUserName] = useState('');
    const [companyName, setCompanyName] = useState('Azul Handling');
    const [details, setDetails] = useState('');
    const [generatedText, setGeneratedText] = useState('');
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleGenerate = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const res = await fetch(`${API_URL}/api/reclamaciones/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type,
                    user_name: userName,
                    company_name: companyName,
                    details
                })
            });

            if (res.ok) {
                const data = await res.json();
                setGeneratedText(data.content);
            }
        } catch (error) {
            console.error("Error generating claim", error);
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(generatedText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="max-w-5xl mx-auto grid lg:grid-cols-2 gap-8 pb-12">

            {/* Input Form */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-xl">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
                        <PenTool size={20} />
                    </div>
                    <h2 className="text-xl font-bold text-white">Generar Escrito</h2>
                </div>

                <form onSubmit={handleGenerate} className="space-y-4">
                    <div className="space-y-1">
                        <label className="text-sm font-medium text-slate-300">Tipo de Reclamación</label>
                        <select
                            value={type}
                            onChange={e => setType(e.target.value)}
                            className="w-full bg-slate-800/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-indigo-500/50"
                        >
                            <option value="vacaciones">Solicitud de Vacaciones</option>
                            <option value="nomina">Reclamación de Nómina</option>
                            <option value="horario">Modificación de Horario</option>
                            <option value="generico">Generico</option>
                        </select>
                    </div>

                    <div className="space-y-1">
                        <label className="text-sm font-medium text-slate-300">Tu Nombre Completo</label>
                        <input
                            type="text"
                            value={userName}
                            onChange={e => setUserName(e.target.value)}
                            placeholder="Juan Pérez García"
                            className="w-full bg-slate-800/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-indigo-500/50"
                            required
                        />
                    </div>

                    <div className="space-y-1">
                        <label className="text-sm font-medium text-slate-300">Empresa</label>
                        <input
                            type="text"
                            value={companyName}
                            onChange={e => setCompanyName(e.target.value)}
                            className="w-full bg-slate-800/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-indigo-500/50"
                        />
                    </div>

                    <div className="space-y-1">
                        <label className="text-sm font-medium text-slate-300">Detalles Específicos</label>
                        <textarea
                            value={details}
                            onChange={e => setDetails(e.target.value)}
                            placeholder="Describa aquí las fechas solicitadas o los conceptos erróneos..."
                            rows={5}
                            className="w-full bg-slate-800/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-indigo-500/50 resize-none"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-bold text-white transition-all shadow-lg hover:shadow-indigo-500/25 flex items-center justify-center gap-2"
                    >
                        {loading ? 'Generando...' : 'Generar Documento'}
                    </button>
                </form>
            </div>

            {/* Preview Panel */}
            <div className="relative">
                <div className="absolute inset-0 bg-indigo-500/5 rounded-3xl blur-3xl -z-10"></div>

                <div className="h-full bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-xl flex flex-col">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
                                <FileText size={20} />
                            </div>
                            <h2 className="text-xl font-bold text-white">Vista Previa</h2>
                        </div>
                        {generatedText && (
                            <button
                                onClick={copyToClipboard}
                                className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors"
                                title="Copiar al portapapeles"
                            >
                                {copied ? <Check size={20} className="text-emerald-400" /> : <Copy size={20} />}
                            </button>
                        )}
                    </div>

                    <div className="flex-1 bg-white/5 rounded-xl p-6 font-mono text-sm text-slate-300 overflow-y-auto whitespace-pre-wrap border border-white/5">
                        {generatedText ? generatedText : (
                            <div className="h-full flex flex-col items-center justify-center text-slate-600 opacity-60">
                                <p>Rellena el formulario para generar tu escrito</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

        </div>
    );
}
