'use client';

import { motion } from 'framer-motion';
import { Bot, BookOpen, Sparkles, User } from 'lucide-react';

interface KnowledgeItem {
    id: string;
    category: string;
    topic: string;
    content: string;
}

interface MessageBubbleProps {
    content: string;
    role: 'user' | 'assistant';
    sources?: KnowledgeItem[];
}

export default function MessageBubble({ content, role, sources }: MessageBubbleProps) {
    const isUser = role === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-6`}
        >
            <div className={`flex max-w-[90%] md:max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end gap-3`}>

                {/* Avatar Tiny */}
                {!isUser && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-slate-800/50 border border-white/5 flex items-center justify-center text-cyan-400 mb-1 shadow-sm">
                        <Sparkles size={14} />
                    </div>
                )}
                {isUser && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 flex items-center justify-center text-white mb-1 shadow-lg shadow-purple-500/20">
                        <User size={14} />
                    </div>
                )}

                <div className={`flex flex-col gap-1.5 ${isUser ? 'items-end' : 'items-start'}`}>
                    {/* Bubble */}
                    <div className={`px-5 py-3.5 rounded-2xl text-[15px] leading-relaxed shadow-md backdrop-blur-sm ${isUser
                        ? 'bg-gradient-to-br from-cyan-600 to-blue-600 text-white rounded-br-sm border border-cyan-400/20'
                        : 'bg-slate-900/60 border border-white/10 text-slate-200 rounded-bl-sm shadow-[0_4px_10px_rgba(0,0,0,0.1)]'
                        }`}>
                        {content}
                    </div>

                    {/* Sources (AI Only) */}
                    {sources && sources.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-1">
                            {sources.map((source, i) => (
                                <span key={i} className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-900/40 border border-white/5 hover:border-cyan-500/30 rounded-full text-[10px] text-slate-400 font-medium transition-colors cursor-help">
                                    <BookOpen size={10} className="text-cyan-500/70" />
                                    {source.topic.substring(0, 30)}{source.topic.length > 30 ? '...' : ''}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
