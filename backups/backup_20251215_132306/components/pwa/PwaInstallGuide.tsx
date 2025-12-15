'use client';

import { useState, useEffect } from 'react';
import { X, Share, Smartphone, Menu as MenuIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function PwaInstallGuide({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    const [platform, setPlatform] = useState<'ios' | 'android' | 'desktop'>('desktop');

    useEffect(() => {
        const userAgent = window.navigator.userAgent.toLowerCase();
        if (/iphone|ipad|ipod/.test(userAgent)) {
            setPlatform('ios');
        } else if (/android/.test(userAgent)) {
            setPlatform('android');
        } else {
            setPlatform('desktop');
        }
    }, []);

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
                    <motion.div
                        initial={{ opacity: 0, y: 100 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 100 }}
                        className="w-full max-w-sm bg-[var(--card-bg)] border border-[var(--card-border)] rounded-2xl p-6 shadow-2xl relative"
                        onClick={e => e.stopPropagation()}
                    >
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                        >
                            <X size={20} />
                        </button>

                        <div className="text-center space-y-4">
                            <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                                <Smartphone size={32} className="text-white" />
                            </div>

                            <h2 className="text-xl font-bold text-[var(--text-primary)]">Instalar Aplicación</h2>

                            <p className="text-sm text-[var(--text-secondary)]">
                                Instala Asistente Handling para usarlo a pantalla completa y sin conexión.
                            </p>

                            <div className="mt-6 bg-[var(--bg-primary)] rounded-xl p-4 text-left border border-[var(--panel-border)]">
                                {platform === 'ios' && (
                                    <ol className="space-y-3 text-sm text-[var(--text-primary)]">
                                        <li className="flex items-start gap-3">
                                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-[var(--card-border)] flex items-center justify-center text-xs font-bold">1</span>
                                            <span>Pulsa el botón <strong>Compartir</strong> <Share size={14} className="inline mx-1" /> en la barra inferior.</span>
                                        </li>
                                        <li className="flex items-start gap-3">
                                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-[var(--card-border)] flex items-center justify-center text-xs font-bold">2</span>
                                            <span>Busca y selecciona <strong>"Añadir a pantalla de inicio"</strong>.</span>
                                        </li>
                                        <li className="flex items-start gap-3">
                                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-[var(--card-border)] flex items-center justify-center text-xs font-bold">3</span>
                                            <span>Confirma pulsando <strong>Añadir</strong> arriba a la derecha.</span>
                                        </li>
                                    </ol>
                                )}

                                {platform === 'android' && (
                                    <ol className="space-y-3 text-sm text-[var(--text-primary)]">
                                        <li className="flex items-start gap-3">
                                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-[var(--card-border)] flex items-center justify-center text-xs font-bold">1</span>
                                            <span>Pulsa el menú de <strong>3 puntos</strong> <MenuIcon size={14} className="inline mx-1" /> arriba a la derecha.</span>
                                        </li>
                                        <li className="flex items-start gap-3">
                                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-[var(--card-border)] flex items-center justify-center text-xs font-bold">2</span>
                                            <span>Selecciona <strong>"Instalar aplicación"</strong> o "Añadir a pantalla de inicio".</span>
                                        </li>
                                    </ol>
                                )}

                                {platform === 'desktop' && (
                                    <div className="text-center text-sm text-[var(--text-secondary)]">
                                        Esta funcionalidad está pensada para móviles. En tu PC, busca el icono de instalar (+) en la barra de direcciones de Chrome/Edge.
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
