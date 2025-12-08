'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Menu, X, MessageSquare, ShieldCheck, Sparkles, BrainCircuit } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import MessageBubble from './MessageBubble';
import CompanyDropdown from './CompanyDropdown';
import { askAI } from '@/lib/ai-service';
import { type KnowledgeItem, type CompanyId } from '@/data/knowledge-base';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    sources?: KnowledgeItem[];
}

export default function ChatInterface() {
    const [selectedCompanyId, setSelectedCompanyId] = useState<CompanyId | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-mensaje al cambiar empresa
    const handleCompanySelect = (companyId: CompanyId) => {
        setSelectedCompanyId(companyId);
        setMessages([
            {
                id: `welcome-${Date.now()}`,
                role: 'assistant',
                content: `Sistema conectado. Estoy listo para analizar tu convenio.` // Simplified as we don't have company name here easily yet
            }
        ]);
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        if (!selectedCompanyId) {
            alert("Por favor selecciona una empresa primero.");
            return;
        }

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await askAI(userMessage.content, selectedCompanyId);

            const aiMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: response.answer,
                sources: response.sources.map((s: any, i: number) => ({
                    ...s,
                    id: s.id || `source-${Date.now()}-${i}`,
                    keywords: s.keywords || [],
                    scope: s.scope || 'global'
                }))
            };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error("Error AI:", error);
            // Fallback message
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                content: "Lo siento, hubo un error de conexión con el núcleo de IA. Inténtalo de nuevo."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex h-full rounded-3xl overflow-hidden glass-panel border-0 shadow-2xl relative">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-gradient-to-br from-slate-900/80 via-slate-950/90 to-slate-900/80 -z-10"></div>

            {/* SIDEBAR (Desktop) */}
            <aside className="hidden md:flex flex-col w-80 bg-black/20 backdrop-blur-md border-r border-white/5 h-full">
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="w-10 h-10 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
                            <BrainCircuit size={22} />
                        </div>
                        <div>
                            <h1 className="font-bold text-lg text-white tracking-tight leading-none">LegalAI</h1>
                            <span className="text-[10px] text-cyan-400 font-medium tracking-wider uppercase">Enterprise Edition</span>
                        </div>
                    </div>

                    <div className="mb-8 space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-1">
                            Contexto Legal
                        </label>
                        <CompanyDropdown selectedCompanyId={selectedCompanyId} onSelect={handleCompanySelect} />
                    </div>

                    <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin">
                        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 px-1">
                            Memoria Reciente
                        </div>
                        <div className="p-4 rounded-xl border border-white/5 bg-white/[0.02] text-xs text-slate-500 text-center py-6">
                            No hay consultas previas en esta sesión.
                        </div>
                    </div>
                </div>
                <div className="p-4 border-t border-white/5">
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                        Sistema Operativo v2.1
                    </div>
                </div>
            </aside>

            {/* MAIN CONTENT */}
            <main className="flex-1 flex flex-col h-full relative">
                {/* MOBILE HEADER */}
                <header className="md:hidden flex items-center justify-between p-4 border-b border-white/5 bg-slate-950/50 backdrop-blur-md z-20">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-cyan-600 rounded-lg flex items-center justify-center text-white">
                            <BrainCircuit size={18} />
                        </div>
                        <span className="font-bold text-white">LegalAI</span>
                    </div>
                    <div className="w-40">
                        <CompanyDropdown selectedCompanyId={selectedCompanyId} onSelect={handleCompanySelect} />
                    </div>
                </header>

                {/* CHAT AREA */}
                <div className="flex-1 relative flex flex-col overflow-hidden">

                    {!selectedCompanyId && messages.length === 0 ? (
                        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-slate-400 z-10">
                            <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center mb-6 border border-white/5 shadow-2xl shadow-cyan-500/10">
                                <Sparkles size={32} className="text-cyan-400" />
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-2">Asistente Jurídico Conectado</h3>
                            <p className="max-w-xs mx-auto text-slate-500 text-sm leading-relaxed">
                                Selecciona el convenio colectivo (empresa) para cargar la normativa vigente y comenzar el análisis.
                            </p>
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
                                    <div className="flex items-center gap-3 text-cyan-400 text-sm ml-4">
                                        <div className="flex gap-1">
                                            <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></span>
                                            <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                                            <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                                        </div>
                                        Analizando normativa...
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="p-4 md:p-6 z-20">
                        <div className="max-w-3xl mx-auto">
                            <form onSubmit={handleSubmit} className="relative flex items-center bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-2xl p-2 focus-within:ring-1 focus-within:ring-cyan-500/50 focus-within:border-cyan-500/50 transition-all shadow-xl">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder={selectedCompanyId ? "Escribe tu pregunta..." : "Selecciona una empresa para activar el chat..."}
                                    className="flex-1 bg-transparent border-none focus:outline-none text-slate-200 placeholder:text-slate-600 px-4 py-3 text-base"
                                    disabled={isLoading}
                                />
                                <button
                                    type="submit"
                                    disabled={!input.trim() || isLoading}
                                    className="p-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl hover:shadow-[0_0_15px_rgba(6,182,212,0.4)] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
                                >
                                    <Send size={20} />
                                </button>
                            </form>
                            <div className="text-center mt-3">
                                <p className="text-[10px] text-slate-600 uppercase tracking-wider">
                                    IA entrenada con normativas oficiales BOE
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
