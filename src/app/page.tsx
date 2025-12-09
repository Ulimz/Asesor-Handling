'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ShieldCheck, MessageSquare, ArrowRight, Zap, Globe, Lock } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen text-slate-100 font-sans selection:bg-cyan-500/30">

      {/* NAVBAR */}
      <nav className="fixed top-0 inset-x-0 z-50 h-20 flex items-center bg-slate-950/50 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto w-full px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
              <ShieldCheck size={20} strokeWidth={2.5} />
            </div>
            <span className="font-bold text-xl tracking-tight text-white">
              Legal<span className="text-cyan-400">AI</span>
            </span>
          </div>

          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#features" className="hover:text-cyan-400 transition-colors">Funcionalidades</a>
            <a href="#how-it-works" className="hover:text-cyan-400 transition-colors">Cómo funciona</a>
          </div>

          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">
              Login
            </Link>
            <Link href="/login" className="px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 text-white text-sm font-bold rounded-full hover:shadow-lg hover:shadow-cyan-500/25 transition-all flex items-center gap-2">
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
            IA Jurídica para Handling Aeroportuario
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-6xl md:text-8xl font-black tracking-tight text-white mb-8 leading-[1.1]"
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
            className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto mb-12 leading-relaxed font-light"
          >
            Olvídate del lenguaje legal complejo. Pregunta a nuestra IA experta en el sector handling y obtén respuestas <span className="text-white font-medium">inmediatas y precisas</span> sobre tus derechos.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-6"
          >
            <Link href="/login" className="group w-full sm:w-auto px-8 py-4 bg-white text-slate-950 rounded-full font-bold text-lg hover:bg-cyan-50 transition-all shadow-[0_0_40px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_rgba(0,229,255,0.4)] flex items-center justify-center gap-3">
              <MessageSquare size={20} className="group-hover:text-cyan-600 transition-colors" />
              Hablar con la IA
            </Link>
            <a href="#demo" className="text-slate-400 hover:text-white font-medium flex items-center gap-2 transition-colors">
              Ver Demo <ArrowRight size={18} />
            </a>
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
              <div key={i} className="glass-card p-8 rounded-3xl bg-slate-900/40 border border-white/5 hover:border-cyan-500/30 hover:bg-slate-800/50 group">
                <div className="w-14 h-14 bg-slate-950 rounded-2xl flex items-center justify-center mb-6 border border-white/10 group-hover:border-cyan-500/30 group-hover:shadow-[0_0_20px_rgba(0,229,255,0.1)] transition-all">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-slate-400 leading-relaxed">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-12 border-t border-white/5 text-center text-slate-500 text-sm">
        <p>© 2024 LegalAI Handling. Inteligencia Artificial al servicio del trabajador.</p>
      </footer>

    </div>
  );
}
