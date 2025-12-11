import React from 'react';

export default function LegalNoticePage() {
    return (
        <div className="min-h-screen bg-slate-950 text-slate-300 py-12 px-4 md:px-8">
            <div className="max-w-4xl mx-auto space-y-8">
                <header className="border-b border-slate-800 pb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Aviso Legal</h1>
                    <p className="text-slate-400">Información general para dar cumplimiento a la Ley 34/2002 (LSSI).</p>
                </header>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white">1. Datos Identificativos</h2>
                    <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
                        <p className="mb-4">En cumplimiento con el deber de información recogido en artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad de la Información y del Comercio Electrónico, a continuación se reflejan los siguientes datos:</p>
                        <ul className="space-y-2 text-sm">
                            <li><strong className="text-white">Titular del dominio:</strong> Ulises Muñoz Zapata</li>
                            <li><strong className="text-white">Domicilio:</strong> Alicante, España</li>
                            <li><strong className="text-white">Correo electrónico de contacto:</strong> soporte_asistentehandling@outlook.es</li>
                        </ul>
                    </div>
                </section>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white">2. Usuarios</h2>
                    <p>
                        El acceso y/o uso de este portal atribuye la condición de USUARIO, que acepta, desde dicho acceso y/o uso, las Condiciones Generales de Uso aquí reflejadas.
                    </p>
                </section>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white text-amber-400 flex items-center gap-2">
                        <span>⚠️</span> 3. Exención de Responsabilidad (Uso de IA)
                    </h2>
                    <div className="bg-amber-950/20 border border-amber-900/50 p-6 rounded-xl text-amber-100/80">
                        <p className="mb-4 font-medium">IMPORTANTE:</p>
                        <p className="mb-4">
                            Esta aplicación utiliza sistemas de Inteligencia Artificial (IA) para facilitar la búsqueda y análisis de convenios colectivos. Aunque nos esforzamos por garantizar la precisión de la información:
                        </p>
                        <ul className="list-disc list-inside space-y-2 ml-4">
                            <li>La IA puede cometer errores, alucinaciones o interpretaciones inexactas ("alucinaciones").</li>
                            <li>La información proporcionada por el asistente es puramente informativa y <strong>NO sustituye al asesoramiento legal profesional</strong>.</li>
                            <li>El titular de la web no se hace responsable de las decisiones tomadas basándose únicamente en las respuestas del asistente virtual.</li>
                            <li>Se recomienda encarecidamente verificar cualquier cálculo o información crítica con las fuentes oficiales o un asesor laboral.</li>
                        </ul>
                    </div>
                </section>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white">4. Propiedad Intelectual e Industrial</h2>
                    <p>
                        Todos los contenidos de la web (textos, gráficos, logos, código fuente) son propiedad exclusiva del titular o de terceros que han autorizado su uso, estando protegidos por la legislación sobre Propiedad Intelectual.
                    </p>
                </section>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white">5. Modificaciones</h2>
                    <p>
                        El titular se reserva el derecho de efectuar sin previo aviso las modificaciones que considere oportunas en su portal, pudiendo cambiar, suprimir o añadir tanto los contenidos y servicios que se presten a través de la misma como la forma en la que éstos aparezcan presentados.
                    </p>
                </section>
            </div >
        </div >
    );
}
