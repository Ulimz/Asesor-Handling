'use client';

import Link from 'next/link';
import Image from 'next/image';
import NeonLogo from '@/components/NeonLogo';
import BrandLogo from '@/components/BrandLogo';
import ThemeToggle from '@/components/ThemeToggle';
import { motion } from 'framer-motion';
import { ArrowRight, MessageSquare, ShieldCheck, Scale, History, UserCheck, CheckCircle2, Zap, Globe, Lock } from 'lucide-react';
import { companies } from '@/data/knowledge-base';

export default function LandingPage() {
  return (
    <div className="min-h-screen text-[var(--text-primary)] font-sans selection:bg-cyan-500/30 transition-colors duration-300">

      {/* NAVBAR */}
      <nav className="fixed top-0 inset-x-0 z-50 h-16 md:h-20 flex items-center bg-[var(--bg-primary)]/80 backdrop-blur-xl border-b border-[var(--panel-border)] transition-colors duration-300">
        <div className="max-w-7xl mx-auto w-full px-4 md:px-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* Mobile Logo */}
            <div className="md:hidden">
              <BrandLogo iconSize={32} textSize="sm" />
            </div>
            {/* Desktop Logo */}
            <div className="hidden md:block">
              <BrandLogo iconSize={64} textSize="xl" />
            </div>
          </div>

          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-[var(--text-secondary)]">
            {/* Links removed as per user request */}
          </div>

          <div className="flex items-center gap-2 md:gap-4">
            <div className="md:hidden scale-90">
              <ThemeToggle />
            </div>
            <Link href="/login" className="hidden md:block text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              Login
            </Link>
            <Link href="/login" className="px-3 py-2 md:px-5 md:py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 text-white text-[10px] md:text-sm font-bold rounded-full hover:shadow-lg hover:shadow-cyan-500/25 transition-all flex items-center gap-1.5 md:gap-2">
              Empezar Gratis
            </Link>
          </div>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section className="relative pt-40 pb-32 px-6 overflow-hidden">
        <div className="max-w-5xl mx-auto text-center relative z-10">

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-950/30 border border-cyan-500/30 text-cyan-400 text-xs font-bold mb-8 backdrop-blur-md"
          >
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(34,211,238,0.5)]"></span>
            IA Asistente Handling Aeroportuario
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl sm:text-6xl md:text-8xl font-black tracking-tight text-[var(--text-primary)] mb-8 leading-[1.1]"
          >
            Tu Convenio, <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 drop-shadow-[0_0_30px_rgba(0,229,255,0.3)]">
              Descodificado.
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl md:text-2xl text-[var(--text-secondary)] max-w-3xl mx-auto mb-12 leading-relaxed font-light"
          >
            Olvídate del lenguaje legal complejo. Pregunta a nuestra IA experta en el sector handling y obtén respuestas <span className="text-[var(--text-primary)] font-medium">inmediatas y precisas</span> sobre tus derechos.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-6"
          >
            <Link href="/login" className="group w-full sm:w-auto px-8 py-4 bg-[var(--text-primary)] text-[var(--bg-primary)] rounded-full font-bold text-lg hover:bg-cyan-50 transition-all shadow-[0_0_40px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_rgba(0,229,255,0.4)] flex items-center justify-center gap-3">
              <MessageSquare size={20} className="group-hover:text-cyan-600 transition-colors" />
              Hablar con la IA
            </Link>
            {/* Demo link removed */}
          </motion.div>
        </div>
      </section>

      {/* FEATURES GRID */}
      <section className="py-24 px-6 relative" id="features">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: <Zap className="text-cyan-400" />,
                title: "Respuestas al Instante",
                desc: "No esperes días a una respuesta sindical. Tu asistente trabaja 24/7 para resolver dudas de nómina y turnos."
              },
              {
                icon: <Globe className="text-purple-400" />,
                title: "Multiconvenio",
                desc: "Base de datos actualizada con normativas de Iberia, Groundforce, Swissport, Menzies y más."
              },
              {
                icon: <Lock className="text-emerald-400" />,
                title: "Privacidad Total",
                desc: "Tus consultas son anónimas. No guardamos datos personales, solo te ayudamos a entender tus derechos."
              }
            ].map((feature, i) => (
              <div key={i} className="glass-card p-8 rounded-3xl group">
                <div className="w-14 h-14 bg-[var(--bg-primary)] rounded-2xl flex items-center justify-center mb-6 border border-[var(--panel-border)] group-hover:border-cyan-500/30 group-hover:shadow-[0_0_20px_rgba(0,229,255,0.1)] transition-all">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-[var(--text-primary)] mb-3">{feature.title}</h3>
                <p className="text-[var(--text-secondary)] leading-relaxed">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CONVENIOS SECTION */}
      <section className="py-20 px-6 border-t border-[var(--panel-border)] bg-[var(--panel-bg)]/50 transition-colors duration-300" id="convenios">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-12">Convenios Disponibles</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 opacity-100 max-w-5xl mx-auto">
            {/* Updated list based on DB data - Corrected per user feedback */}
            {companies.map((company) => (
              <div key={company.id} className="px-6 py-3 rounded-xl border border-[var(--panel-border)] bg-[var(--card-bg)] text-[var(--text-secondary)] font-bold tracking-wider hover:border-cyan-500/30 hover:text-[var(--text-primary)] transition-all cursor-default shadow-lg shadow-black/5 uppercase">
                {company.name}
              </div>
            ))}
          </div>
          <p className="mt-8 text-[var(--text-secondary)] text-sm">
            ¿No encuentras el tuyo?{' '}
            <a href="mailto:soporte_asistentehandling@outlook.es?subject=Solicitud de Nuevo Convenio" className="text-cyan-400 cursor-pointer hover:underline hover:text-cyan-300 transition-colors">
              Solicita que lo añadamos.
            </a>
          </p>
        </div>
      </section>

      {/* FAQ SECTION */}
      <section className="py-24 px-6 relative" id="faq">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-12 text-center">Preguntas Frecuentes</h2>
          <div className="space-y-6">
            {[
              {
                q: "¿La información tiene validez legal?",
                a: "No. Esta es una herramienta informativa. Aunque entrenada con los convenios oficiales, puede cometer errores. Para acciones legales, consulta siempre con tu sindicato."
              },
              {
                q: "¿Guardáis mis conversaciones?",
                a: "No almacenamos datos personales. Tu historial se guarda localmente en tu navegador para que puedas consultarlo durante la sesión, pero priorizamos tu privacidad."
              },
              {
                q: "¿Es gratuito?",
                a: "Sí, la versión básica de consulta de convenios es totalmente gratuita para los trabajadores del sector."
              }
            ].map((faq, i) => (
              <div key={i} className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-2xl p-6 hover:border-cyan-500/20 transition-colors duration-300 shadow-sm">
                <h3 className="font-bold text-[var(--text-primary)] mb-2 text-lg">{faq.q}</h3>
                <p className="text-[var(--text-secondary)] leading-relaxed text-sm">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-12 border-t border-[var(--panel-border)] text-center text-[var(--text-secondary)] text-sm transition-colors duration-300">
        <p className="mb-2">© 2024 Asistente IA Handling. Inteligencia Artificial al servicio del trabajador.</p>
        <p className="text-xs text-[var(--text-secondary)]/70 max-w-2xl mx-auto">
          AVISO: Esta herramienta no tiene validez jurídica. Las respuestas son generadas por Inteligencia Artificial basada en convenios y están destinadas únicamente a fines informativos y de orientación. Ante duda legal, consulte con un representante sindical o abogado.
        </p>
      </footer>

    </div>
  );
}
