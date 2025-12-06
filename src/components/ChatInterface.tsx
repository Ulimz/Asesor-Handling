'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Menu, X, MessageSquare, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';
import MessageBubble from './MessageBubble';
import CompanyDropdown from './CompanyDropdown';
import { askAI } from '@/lib/ai-service';
import { companies, type KnowledgeItem, type CompanyId } from '@/data/knowledge-base';

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
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const selectedCompany = companies.find(c => c.id === selectedCompanyId);

    // Auto-mensaje al cambiar empresa
    const handleCompanySelect = (companyId: CompanyId) => {
        setSelectedCompanyId(companyId);
        setMessages([
            {
                id: `welcome-${Date.now()}`,
                role: 'assistant',
                content: `Cargando normativa de ${companies.find(c => c.id === companyId)?.name}... Todo listo. ¿Qué quieres saber?`
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

        // Validación visual si no hay empresa seleccionada
        if (!selectedCompanyId) {
            alert("Por favor selecciona una empresa primero en el menú superior izquieda.");
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
                sources: response.sources
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                content: 'Error de conexión. Inténtalo de nuevo.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex h-screen bg-white overflow-hidden">

            {/* SIDEBAR (Desktop) */}
            <aside className="hidden md:flex flex-col w-80 bg-slate-50 border-r border-slate-200 h-full">
                <div className="p-6">
                    <div className="flex items-center gap-2 mb-8">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">
                            <ShieldCheck size={18} />
                        </div>
                        <h1 className="font-bold text-slate-800 tracking-tight">Legal AI Assistant</h1>
                    </div>

                    <div className="mb-6">
                        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
                            Empresa Activa
                        </label>
                        <CompanyDropdown selectedCompanyId={selectedCompanyId} onSelect={handleCompanySelect} />
                    </div>

                    <div className="flex-1 overflow-y-auto">
                        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                            Historial
                        </div>
                        <div className="p-3 bg-white border border-slate-100 rounded-xl text-sm text-slate-500 text-center py-8">
                            Sin historial reciente
                        </div>
                    </div>
                </div>

                <div className="p-4 border-t border-slate-200 text-xs text-slate-400 text-center">
                    v2.1.0 · Connected
                </div>
            </aside>

            {/* MAIN CONTENT */}
            <main className="flex-1 flex flex-col h-full relative">

                {/* MOBILE HEADER */}
                <header className="md:hidden flex items-center justify-between p-4 border-b border-slate-100 bg-white z-20">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">
                            <ShieldCheck size={18} />
                        </div>
                        <h1 className="font-bold text-slate-800">Legal AI</h1>
                    </div>

                    {/* Mobile Dropdown Wrapper */}
                    <div className="w-48">
                        <CompanyDropdown selectedCompanyId={selectedCompanyId} onSelect={handleCompanySelect} />
                    </div>
                </header>

                {/* CHAT AREA */}
                <div className="flex-1 bg-white relative flex flex-col overflow-hidden">
                    {/* Background Pattern */}
                    <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:20px_20px] opacity-30 pointer-events-none"></div>

                    {!selectedCompanyId && messages.length === 0 ? (
                        // Empty State
                        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-slate-400 z-10">
                            <MessageSquare size={48} className="mb-4 text-slate-200" />
                            <h3 className="text-lg font-semibold text-slate-600 mb-2">Bienvenido al Asistente</h3>
                            <p className="max-w-xs mx-auto">Selecciona tu empresa en el menú {isMobileMenuOpen ? 'superior' : 'de la izquierda'} para comenzar.</p>
                        </div>
                    ) : (
                        // Messages List
                        <div className="flex-1 overflow-y-auto p-4 md:p-10 z-10 scrollbar-thin">
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
                                    <div className="flex items-center gap-2 text-slate-400 text-sm ml-4">
                                        <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                                        Escribiendo...
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="p-4 md:p-6 bg-white/80 backdrop-blur-lg border-t border-slate-100 z-20">
                        <div className="max-w-3xl mx-auto relative group">
                            <form onSubmit={handleSubmit} className="relative flex items-center bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-400 transition-all shadow-sm">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder={selectedCompany ? `Pregunta sobre ${selectedCompany.name}...` : "Selecciona una empresa primero..."}
                                    className="flex-1 bg-transparent border-none focus:outline-none text-slate-800 placeholder:text-slate-400"
                                    disabled={isLoading}
                                />
                                <button
                                    type="submit"
                                    disabled={!input.trim() || isLoading}
                                    className="p-2 bg-white text-blue-600 rounded-xl hover:bg-blue-50 transition-colors shadow-sm border border-slate-100 disabled:opacity-50 disabled:cursor-not-allowed ml-2"
                                >
                                    <Send size={18} />
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
