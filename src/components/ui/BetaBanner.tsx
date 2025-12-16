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
                className="bg-amber-500/10 border-b border-amber-500/20 backdrop-blur-md relative z-50"
            >
                <div className="max-w-7xl mx-auto px-4 py-2 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 text-amber-500 text-xs md:text-sm font-medium">
                        <AlertTriangle size={16} className="shrink-0" />
                        <p>
                            <span className="font-bold">BETA ABIERTA:</span> Estamos en mantenimiento y actualización constante. Es posible que experimentes errores puntuales. Disculpen las molestias.
                        </p>
                    </div>
                    <button
                        onClick={() => setIsVisible(false)}
                        className="p-1 hover:bg-amber-500/10 rounded-full transition-colors text-amber-500/70 hover:text-amber-500"
                    >
                        <X size={14} />
                    </button>
                </div>
            </motion.div>
        </AnimatePresence>
    );
}
