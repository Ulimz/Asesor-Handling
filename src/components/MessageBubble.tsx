'use client';

import { motion } from 'framer-motion';
import { Bot, User, BookOpen } from 'lucide-react';

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
            <div className={`flex max-w-[90%] md:max-w-[75%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end gap-2`}>

                {/* Avatar Tiny */}
                {!isUser && (
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mb-1">
                        <Bot size={14} />
                    </div>
                )}

                <div className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
                    {/* Bubble */}
                    <div className={`px-4 py-2.5 rounded-2xl text-[15px] shadow-sm leading-relaxed ${isUser
                            ? 'bg-blue-600 text-white rounded-br-sm'
                            : 'bg-white border border-slate-100 text-slate-800 rounded-bl-sm'
                        }`}>
                        {content}
                    </div>

                    {/* Sources (AI Only) */}
                    {sources && sources.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-2">
                            {sources.map((source, i) => (
                                <span key={i} className="inline-flex items-center gap-1 px-2 py-1 bg-slate-50 border border-slate-200 rounded-md text-[10px] text-slate-500 font-medium">
                                    <BookOpen size={10} />
                                    {source.topic.substring(0, 25)}{source.topic.length > 25 ? '...' : ''}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
