'use client';

import { AlertTriangle, X } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function MaintenanceBanner() {
    const [isVisible, setIsVisible] = useState(true);

    if (!isVisible) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="w-full bg-amber-500/10 border-b border-amber-500/20 text-amber-200"
            >
                <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />
                        <p className="text-sm font-medium">
                            <span className="font-bold">Actualización en curso:</span> Estamos implementando mejoras importantes. Es posible que el servicio experimente inestabilidad momentánea.
                        </p>
                    </div>
                    <button
                        onClick={() => setIsVisible(false)}
                        className="p-1 hover:bg-amber-500/20 rounded-lg transition-colors"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            </motion.div>
        </AnimatePresence>
    );
}
