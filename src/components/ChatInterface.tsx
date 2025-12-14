'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Menu, X, MessageSquare, ShieldCheck, Sparkles, BrainCircuit, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import MessageBubble from './MessageBubble';
import { askAI } from '@/lib/ai-service';
import { type KnowledgeItem, type CompanyId, companies } from '@/data/knowledge-base';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    sources?: KnowledgeItem[];
}

interface ChatInterfaceProps {
    selectedCompanyId: CompanyId | null;
}

export default function ChatInterface({ selectedCompanyId }: ChatInterfaceProps) {
    // const [selectedCompanyId, setSelectedCompanyId] = useState<CompanyId | null>(null); <--- Removed internal state
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [recentQueries, setRecentQueries] = useState<string[]>([]);
    const [user, setUser] = useState<any | null>(null); // Using any to avoid importing User type if not easy, but ideally import it. 
    // Actually, I can import { User } from '@/lib/api-service'.
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Optimized scroll - only when messages length changes
    useEffect(() => {
        if (messages.length > 0) {
            const timeout = setTimeout(() => {
                messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            }, 100);
            return () => clearTimeout(timeout);
        }
    }, [messages.length]);

    // Load user profile
    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            import('@/lib/api-service').then(({ apiService }) => {
                apiService.getMe(token).then(u => {
                    setUser(u);
                }).catch(console.error);
            });
        }
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        // Clear previous errors
        setError(null);

        if (!selectedCompanyId) {
            setMessages(prev => [...prev, {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: "⚠️ Por favor selecciona una empresa primero para poder ayudarte con tu consulta."
            }]);
            return;
        }

        const userMessage: Message = {
            id: crypto.randomUUID(),
            role: 'user',
            content: input
        };

        setMessages(prev => [...prev, userMessage]);
        setRecentQueries(prev => [input, ...prev].slice(0, 10));
        setInput('');
        setIsLoading(true);

        try {
            // Pass the entire conversation history (including the new user message)
            const userContext = user ? {
                job_group: user.job_group,
                salary_level: user.salary_level,
                preferred_name: user.preferred_name,
                contract_type: user.contract_type
            } : undefined;

            const response = await askAI([...messages, userMessage], selectedCompanyId!, userContext);

            const aiMessage: Message = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: response.answer,
                sources: response.sources.map((s: any, i: number) => ({
                    ...s,
                    id: s.id || crypto.randomUUID(),
                    keywords: s.keywords || [],
                    scope: s.scope || 'global'
                }))
            };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            if (process.env.NODE_ENV !== 'production') {
                console.error("Error AI:", error);
            }
            // Fallback message
            setMessages(prev => [...prev, {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: "Lo siento, hubo un error de conexión con el núcleo de IA. Inténtalo de nuevo."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex h-full md:rounded-3xl overflow-hidden glass-panel border-0 shadow-none md:shadow-2xl relative">
            {/* Background Effects */}
            {/* Background Effects */}
            <div className="absolute inset-0 bg-gradient-to-br from-[var(--bg-primary)]/80 via-[var(--bg-primary)]/90 to-[var(--bg-primary)]/80 -z-10 transition-colors duration-300"></div>

            {/* SIDEBAR (Desktop) */}
            <aside className="hidden md:flex flex-col w-80 shrink-0 bg-slate-950 border-r border-slate-800 h-full shadow-xl z-20">
                <div className="p-6">


                    <div className="mb-8 space-y-2">
                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-1">
                            Contexto Legal
                        </label>
                        {/* Company Selector Removed - Using Prop */}
                        <div className={`px-4 py-3 rounded-xl border text-sm font-medium transition-all ${selectedCompanyId
                            ? 'bg-sky-500/10 border-sky-500/20 text-sky-400'
                            : 'bg-slate-900/50 border-slate-800 text-slate-500 border-dashed'
                            }`}>
                            {selectedCompanyId ? (
                                <div className="flex items-center gap-2">
                                    <ShieldCheck size={16} />
                                    <span className="capitalize">
                                        {companies.find(c => c.id === selectedCompanyId)?.agreementLabel || selectedCompanyId}
                                    </span>
                                </div>
                            ) : (
                                "Selecciona empresa arriba ↗"
                            )}
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin">
                        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 px-1">
                            Memoria Reciente
                        </div>
                        {recentQueries.length === 0 ? (
                            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/50 text-xs text-slate-500 text-center py-6">
                                No hay consultas previas en esta sesión.
                            </div>
                        ) : (
                            <div className="space-y-2">
                                {recentQueries.map((q, i) => (
                                    <button
                                        key={i}
                                        onClick={() => setInput(q)}
                                        className="w-full text-left p-3 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 hover:bg-slate-800 text-xs text-slate-400 hover:text-white transition-all truncate group flex items-center gap-2"
                                    >
                                        <div className="w-1.5 h-1.5 rounded-full bg-slate-600 group-hover:bg-sky-500 transition-colors"></div>
                                        {q}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
                <div className="p-4 border-t border-slate-800">
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                        Sistema Operativo v2.2
                    </div>
                </div>
            </aside>

            {/* MAIN CONTENT */}
            <main className="flex-1 flex flex-col h-full relative bg-[var(--bg-primary)] min-w-0 transition-colors duration-300">
                {/* MOBILE HEADER */}
                <header className="md:hidden flex items-center justify-between p-4 border-b border-[var(--panel-border)] bg-[var(--bg-primary)] z-20 transition-colors duration-300">

                    {/* Mobile Selector Removed */}
                </header>

                {/* CHAT AREA */}
                <div className="flex-1 relative flex flex-col overflow-hidden">

                    {!selectedCompanyId && messages.length === 0 ? (
                        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-[var(--text-secondary)] z-10">
                            <div className="w-20 h-20 bg-[var(--panel-bg)] rounded-full flex items-center justify-center mb-6 border border-[var(--panel-border)] shadow-xl">
                                <Sparkles size={32} className="text-sky-400" />
                            </div>
                            <h3 className="text-2xl font-bold text-[var(--text-primary)] mb-2">Asistente Jurídico Expert</h3>
                            <p className="max-w-xs mx-auto text-[var(--text-secondary)] text-sm leading-relaxed mb-8">
                                Selecciona tu empresa y pregunta sobre convenios, turnos o nóminas.
                            </p>
                        </div>
                    ) : messages.length === 0 ? (
                        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-[var(--text-secondary)] z-10">
                            <div className="w-16 h-16 bg-[var(--panel-bg)] rounded-2xl flex items-center justify-center mb-6 border border-[var(--panel-border)] text-sky-500">
                                <MessageSquare size={32} />
                            </div>
                            <h3 className="text-xl font-bold text-[var(--text-primary)] mb-2">
                                ¿En qué puedo ayudarte hoy{user?.preferred_name ? `, ${user.preferred_name}` : ''}?
                            </h3>
                            <p className="max-w-md mx-auto text-[var(--text-secondary)] text-sm mb-8">
                                He cargado el convenio de <span className="text-sky-400 font-semibold uppercase">{selectedCompanyId}</span>.
                                Pregúntame sobre cualquier duda legal o laboral.
                            </p>

                            {/* SUGGESTION CHIPS */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg w-full">
                                {[
                                    "¿Cuál es el descanso mínimo entre turnos?",
                                    "¿Cómo se pagan las horas perentorias?",
                                    "¿Cuándo subo de nivel salarial?",
                                    "Días de vacaciones por convenio"
                                ].map((text, i) => (
                                    <button
                                        key={i}
                                        onClick={() => { setInput(text); }}
                                        className="p-3 bg-[var(--card-bg)] hover:bg-[var(--panel-bg)] border border-[var(--panel-border)] hover:border-sky-500/50 rounded-xl text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all text-left flex items-center justify-between group"
                                    >
                                        {text}
                                        <Send size={14} className="opacity-0 group-hover:opacity-100 text-sky-400 transition-opacity" />
                                    </button>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="flex-1 overflow-y-auto p-4 md:p-8 z-10 scrollbar-thin">
                            <div className="max-w-3xl mx-auto space-y-6">
                                {messages.map((msg) => (
                                    <MessageBubble
                                        key={msg.id}
                                        content={msg.content}
                                        role={msg.role}
                                        sources={msg.sources}
                                    />
                                ))}
                                {isLoading && (
                                    <div className="flex items-center gap-3 text-sky-400 text-sm ml-4">
                                        <div className="flex gap-1">
                                            <span className="w-2 h-2 bg-sky-400 rounded-full animate-bounce"></span>
                                            <span className="w-2 h-2 bg-sky-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                                            <span className="w-2 h-2 bg-sky-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                                        </div>
                                        Analizando normativa vigente...
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="p-4 pb-4 md:p-6 z-20 bg-[var(--bg-primary)]/90 backdrop-blur-md border-t border-[var(--panel-border)] transition-colors duration-300">
                        <div className="max-w-3xl mx-auto">
                            <form onSubmit={handleSubmit} className="relative flex items-center bg-[var(--card-bg)] border border-[var(--card-border)] rounded-2xl p-2 focus-within:ring-1 focus-within:ring-sky-500/50 transition-all shadow-lg">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder={selectedCompanyId ? "Escribe tu pregunta jurídica..." : "Selecciona una empresa primero..."}
                                    className="flex-1 bg-transparent border-none focus:outline-none text-[var(--text-primary)] placeholder:text-slate-500 px-4 py-3 text-base"
                                    disabled={isLoading}
                                />
                                <button
                                    type="submit"
                                    disabled={!input.trim() || isLoading}
                                    className="p-3 bg-sky-600 text-white rounded-xl hover:bg-sky-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-sky-900/20"
                                >
                                    {isLoading ? (
                                        <Loader2 size={20} className="animate-spin" />
                                    ) : (
                                        <Send size={20} />
                                    )}
                                </button>
                            </form>
                            <div className="text-center mt-3 space-y-1">
                                <p className="text-[10px] text-slate-500 font-medium">
                                    IA entrenada con Convenios Colectivos. <span className="text-amber-500/80">Puede cometer errores.</span>
                                </p>
                                <p className="text-[9px] text-slate-600">
                                    No introduzcas datos personales sensibles. Consulta nuestras políticas en{' '}
                                    <a href="/privacidad" target="_blank" className="hover:text-sky-400 underline decoration-slate-700 underline-offset-2">Privacidad</a> y{' '}
                                    <a href="/aviso-legal" target="_blank" className="hover:text-sky-400 underline decoration-slate-700 underline-offset-2">Aviso Legal</a>.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
