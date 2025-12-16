'use client';

import { AlertTriangle, X } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function BetaBanner() {
    const [isVisible, setIsVisible] = useState(true);

    if (!isVisible) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, height: 0 }}
                className="fixed top-0 left-0 right-0 z-[100] bg-orange-600 text-white shadow-lg shadow-orange-900/20"
            >
                <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 text-white text-xs md:text-sm font-bold tracking-wide">
                        <AlertTriangle size={18} className="shrink-0 fill-white text-orange-600" />
                        <p>
                            <span className="uppercase">⚠️ Beta Abierta:</span> Estamos en mantenimiento y actualización constante. Servicio inestable.
                        </p>
                    </div>
                    <button
                        onClick={() => setIsVisible(false)}
                        className="p-1 hover:bg-black/20 rounded-full transition-colors text-white/80 hover:text-white"
                    >
                        <X size={16} />
                    </button>
                </div>
            </motion.div>
        </AnimatePresence>
    );
}
