import { motion } from 'framer-motion';
import { Bot, BookOpen, Sparkles, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

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
            <div className={`flex max-w-[95%] md:max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end gap-3`}>

                {/* Avatar Tiny */}
                {!isUser && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-[var(--panel-bg)] border border-[var(--panel-border)] flex items-center justify-center text-cyan-400 mb-1 shadow-sm">
                        <Sparkles size={14} />
                    </div>
                )}
                {isUser && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 flex items-center justify-center text-white mb-1 shadow-lg shadow-purple-500/20">
                        <User size={14} />
                    </div>
                )}

                <div className={`flex flex-col gap-1.5 ${isUser ? 'items-end' : 'items-start'} w-full min-w-0 overflow-hidden`}>
                    {/* Bubble */}
                    <div className={`px-5 py-3.5 rounded-2xl text-[15px] leading-relaxed shadow-md backdrop-blur-sm w-full transition-colors duration-300 ${isUser
                        ? 'bg-gradient-to-br from-cyan-600 to-blue-600 text-white rounded-br-sm border border-cyan-400/20'
                        : 'bg-[var(--card-bg)] border border-[var(--card-border)] text-[var(--text-primary)] rounded-bl-sm shadow-[0_4px_10px_rgba(0,0,0,0.1)]'
                        }`}>
                        {isUser ? (
                            <p>{content}</p>
                        ) : (
                            // Use 'prose' by default (for light mode), and 'dark:prose-invert' for dark mode
                            // We need to ensure prose-slate maps correctly or custom prose colors
                            <div className="prose prose-sm max-w-none dark:prose-invert text-[var(--text-primary)] 
                                prose-p:text-[var(--text-primary)] prose-headings:text-[var(--text-primary)] prose-strong:text-[var(--text-primary)]
                                prose-li:text-[var(--text-primary)] prose-ul:text-[var(--text-primary)]
                                prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-li:my-0.5 prose-table:my-2 
                                prose-td:px-3 prose-td:py-2 prose-th:px-3 prose-th:py-2 
                                prose-th:bg-[var(--panel-bg)] prose-table:border-collapse prose-table:w-full 
                                prose-td:border prose-td:border-[var(--panel-border)] prose-th:border prose-th:border-[var(--panel-border)]">
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    components={{
                                        table: ({ node, ...props }) => (
                                            <div className="overflow-x-auto max-w-full my-2 border border-[var(--panel-border)] rounded-lg">
                                                <table {...props} className="w-full text-left border-collapse" />
                                            </div>
                                        ),
                                        th: ({ node, ...props }) => (
                                            <th {...props} className="bg-[var(--panel-bg)]/80 px-4 py-3 text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider border-b border-[var(--panel-border)] min-w-[100px]" />
                                        ),
                                        td: ({ node, ...props }) => (
                                            <td {...props} className="px-4 py-3 text-sm text-[var(--text-secondary)] border-b border-[var(--panel-border)]/50 min-w-[100px]" />
                                        )
                                    }}
                                >
                                    {content}
                                </ReactMarkdown>
                            </div>
                        )}
                    </div>

                    {/* Sources (AI Only) */}
                    {sources && sources.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-1">
                            {sources.map((source, i) => (
                                <span key={i} className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-[var(--panel-bg)] border border-[var(--panel-border)] hover:border-cyan-500/30 rounded-full text-[10px] text-[var(--text-secondary)] font-medium transition-colors cursor-help">
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
