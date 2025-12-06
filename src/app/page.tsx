'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ShieldCheck, MessageSquare, HeartHandshake, ArrowRight, Plane, Users, Eye } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-blue-100">

      {/* NAVBAR */}
      <nav className="fixed w-full z-50 bg-white/80 backdrop-blur-md border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">
              <ShieldCheck size={18} strokeWidth={2.5} />
            </div>
            <span className="font-bold text-xl tracking-tight">LegalHandling<span className="text-blue-600">.ai</span></span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#derechos" className="hover:text-blue-600 transition-colors">Tus Derechos</a>
            <a href="#privacidad" className="hover:text-blue-600 transition-colors">Privacidad</a>
            <a href="#convenios" className="hover:text-blue-600 transition-colors">Convenios</a>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-sm font-medium text-slate-600 hover:text-slate-900">
              Entrar
            </Link>
            <Link href="/dashboard" className="px-5 py-2.5 bg-blue-600 text-white text-sm font-bold rounded-full hover:bg-blue-700 transition-all flex items-center gap-2 shadow-lg shadow-blue-500/20">
              Consultar Gratis
            </Link>
          </div>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section className="pt-32 pb-20 px-6 relative overflow-hidden">
        <div className="max-w-5xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-orange-50 text-orange-700 text-xs font-bold mb-8 border border-orange-100"
          >
            <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse"></span>
            Defiende tus derechos con información real
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 mb-8 leading-[1.1]"
          >
            Tu Convenio Colectivo <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">explicado fácil.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl md:text-2xl text-slate-500 max-w-3xl mx-auto mb-10 leading-relaxed font-light"
          >
            ¿Dudas sobre tus vacaciones, turnos o nómina? <br />
            <strong className="text-slate-800 font-semibold">No dependas de rumores.</strong> Obtén respuestas inmediatas basadas 100% en la normativa legal de tu empresa de handling.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link href="/dashboard" className="w-full sm:w-auto px-8 py-4 bg-blue-600 text-white rounded-full font-bold text-lg hover:bg-blue-700 transition-all shadow-xl hover:shadow-blue-600/30 flex items-center justify-center gap-2 trasform hover:-translate-y-1">
              <MessageSquare size={20} /> Empezar Chat Anónimo
            </Link>
          </motion.div>

          <div className="mt-16 border-t border-slate-100 pt-8">
            <p className="text-sm text-slate-400 font-medium mb-4">
              Compatible con normativas de:
            </p>
            <div className="flex flex-wrap justify-center gap-6 md:gap-12 opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
              {/* Nombres de empresas como texto simple y elegante */}
              <span className="text-lg font-bold text-slate-700">IBERIA</span>
              <span className="text-lg font-bold text-slate-700">Groundforce</span>
              <span className="text-lg font-bold text-slate-700">Swissport</span>
              <span className="text-lg font-bold text-slate-700">Menzies</span>
              <span className="text-lg font-bold text-slate-700">EasyJet</span>
            </div>
          </div>
        </div>

        {/* Background Grid */}
        <div className="absolute inset-0 -z-10 h-full w-full bg-white [background:radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:16px_16px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,#000_70%,transparent_100%)]"></div>
      </section>

      {/* PROBLEMS / SOLUTIONS */}
      <section className="py-24 bg-slate-50 border-t border-slate-200" id="derechos">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">El poder de saber tus derechos</h2>
            <p className="text-slate-500 max-w-2xl mx-auto text-lg">
              Muchas veces perdemos beneficios simplemente por no saber que existen o por no entender la letra pequeña del convenio.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Eye size={24} />,
                title: "Claridad Total",
                desc: "Olvídate de leer el BOE. Traducimos el lenguaje legal a español claro para que sepas exactamente qué te corresponde."
              },
              {
                icon: <ShieldCheck size={24} />,
                title: "Respaldo Legal",
                desc: "Cada respuesta viene con la cita del artículo exacto. Ve a hablar con tu supervisor con la ley en la mano."
              },
              {
                icon: <Users size={24} />,
                title: "Sin Intermediarios",
                desc: "No esperes a que te responda el enlace sindical. Tienes un experto en tu bolsillo 24/7."
              }
            ].map((feature, i) => (
              <div key={i} className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mb-6">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-500 leading-relaxed">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PRIVACY EMPHASIS */}
      <section className="py-24 px-6 bg-white" id="privacidad">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center gap-12 bg-slate-900 rounded-3xl p-8 md:p-16 text-white shadow-2xl overflow-hidden relative">
          <div className="flex-1 relative z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/20 text-green-300 text-xs font-bold mb-6 border border-green-500/30">
              <ShieldCheck size={12} /> 100% Confidencial
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Tu empresa no sabrá lo que preguntas</h2>
            <p className="text-slate-300 text-lg mb-8 leading-relaxed">
              Sabemos que hay temas delicados. Nuestro sistema no comparte tu historial con RRHH ni con nadie. Pregunta sin miedo sobre despidos, bajas o conflictos.
            </p>
            <Link href="/dashboard" className="text-white border-b border-blue-400 pb-0.5 hover:text-blue-300 transition-colors">
              Leer política de privacidad &rarr;
            </Link>
          </div>
          <div className="flex-1 flex justify-center relative z-10">
            {/* Visual Abstracto de Privacidad */}
            <div className="w-48 h-48 bg-gradient-to-tr from-blue-600 to-purple-600 rounded-2xl rotate-3 flex items-center justify-center shadow-2xl">
              <Lock size={64} className="text-white" />
            </div>
          </div>

          {/* Background details */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-overlay filter blur-[100px] opacity-20"></div>
        </div>
      </section>

      {/* FAQ / CTA FINAL */}
      <section className="py-24 px-6 text-center bg-slate-50 border-t border-slate-200">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-slate-900 mb-6">¿Preparado para conocer tus derechos?</h2>
          <p className="text-slate-500 text-lg mb-10">
            Únete a miles de trabajadores del sector aéreo que ya no tienen dudas sobre su nómina.
          </p>
          <Link href="/dashboard" className="inline-flex items-center gap-2 px-10 py-5 bg-blue-600 text-white rounded-full font-bold text-lg hover:bg-blue-700 transition-all transform hover:scale-105 shadow-xl">
            Hacer mi primera consulta <ArrowRight size={20} />
          </Link>
          <p className="mt-6 text-xs text-slate-400">
            No requiere registro para consultas básicas · Gratuito para trabajadores
          </p>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-white border-t border-slate-100 py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="text-sm text-slate-500">
            © 2024 LegalHandling AI. Hecho para los trabajadores.
          </div>
          <div className="flex gap-6 text-sm font-medium text-slate-600">
            <a href="#" className="hover:text-slate-900">Aviso Legal</a>
            <a href="#" className="hover:text-slate-900">Política de Privacidad</a>
            <a href="#" className="hover:text-slate-900">Contacto</a>
          </div>
        </div>
      </footer>

    </div>
  );
}

function Lock({ size, className }: { size: number, className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  )
}
