'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { X } from 'lucide-react';

export default function CookieBanner() {
    const [show, setShow] = useState(false);

    useEffect(() => {
        // Check if user has already accepted
        const accepted = localStorage.getItem('cookie_consent');
        if (!accepted) {
            setShow(true);
        }
    }, []);

    const accept = () => {
        localStorage.setItem('cookie_consent', 'true');
        setShow(false);
    };

    if (!show) return null;

    return (
        <div className="fixed bottom-0 left-0 right-0 z-50 p-4 md:p-6 bg-slate-900/95 backdrop-blur-md border-t border-slate-700 shadow-2xl animate-in slide-in-from-bottom-10 fade-in duration-500">
            <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">

                <div className="flex-1 text-sm text-slate-300">
                    <p>
                        Usamos cookies propias y de terceros para analizar el tráfico y mostrar publicidad personalizada.
                        Al continuar navegando, aceptas nuestra{' '}
                        <Link href="/privacidad" className="text-sky-400 hover:underline">
                            Política de Privacidad
                        </Link> y{' '}
                        <Link href="/cookies" className="text-sky-400 hover:underline">
                            Política de Cookies
                        </Link>.
                    </p>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                    {/* 
                In a real CMP (like Google's), you would have "Options" here. 
                For this simple version, just Accept.
            */}
                    <button
                        onClick={accept}
                        className="px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white text-sm font-semibold rounded-lg transition-colors shadow-lg shadow-sky-900/20"
                    >
                        Aceptar y Continuar
                    </button>
                    <button
                        onClick={() => setShow(false)}
                        className="p-2 text-slate-400 hover:text-white transition-colors"
                        aria-label="Cerrar"
                    >
                        <X size={20} />
                    </button>
                </div>
            </div>
        </div>
    );
}
