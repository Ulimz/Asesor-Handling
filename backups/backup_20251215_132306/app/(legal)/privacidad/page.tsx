import React from 'react';

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-slate-950 text-slate-300 py-12 px-4 md:px-8">
            <div className="max-w-4xl mx-auto space-y-8">
                <header className="border-b border-slate-800 pb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Política de Privacidad</h1>
                    <p className="text-slate-400">Última actualización: {new Date().toLocaleDateString()}</p>
                </header>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        1. Responsable del Tratamiento
                    </h2>
                    <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 space-y-2">
                        <p>El responsable de los datos recogidos en esta aplicación es:</p>
                        <ul className="list-disc list-inside space-y-1 ml-4 text-slate-400">
                            <li><strong className="text-white">Titular:</strong> Ulises Muñoz Zapata</li>
                            <li><strong className="text-white">Domicilio:</strong> Alicante, España</li>
                            <li><strong className="text-white">Contacto:</strong> soporte_asistentehandling@outlook.es</li>
                        </ul>
                    </div>
                </section>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white">2. Qué datos recopilamos</h2>
                    <p>Para el funcionamiento de la aplicación, tratamos las siguientes categorías de datos:</p>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                        <li>
                            <strong className="text-white">Datos introducidos por el usuario:</strong> Información laboral (categoría profesional, antigüedad) e información económica (salario base, complementos) introducida en la "Calculadora de Nóminas" o el "Generador de Reclamaciones".
                        </li>
                        <li>
                            <strong className="text-white">Interacciones con el Agente IA:</strong> Las consultas de texto enviadas al chat para interpretar el convenio.
                        </li>
                        <li>
                            <strong className="text-white">Datos técnicos y de publicidad:</strong> Identificadores únicos del dispositivo (Advertising ID), dirección IP y datos de uso para la gestión de publicidad y analítica.
                        </li>
                    </ul>
                </section>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white">3. Finalidad del tratamiento</h2>
                    <div className="grid md:grid-cols-3 gap-4">
                        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                            <h3 className="text-white font-semibold mb-2">Funcional</h3>
                            <p className="text-sm">Procesar los cálculos de nómina y generar los documentos de reclamación solicitados.</p>
                        </div>
                        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                            <h3 className="text-white font-semibold mb-2">Asistencia IA</h3>
                            <p className="text-sm">Enviar las consultas anonimizadas a nuestro proveedor de IA para obtener respuestas sobre el convenio colectivo.</p>
                        </div>
                        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                            <h3 className="text-white font-semibold mb-2">Comercial</h3>
                            <p className="text-sm">Mostrar publicidad personalizada o no personalizada a través de redes de anuncios de terceros.</p>
                        </div>
                    </div>
                </section>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white">4. Legitimación</h2>
                    <p>
                        El tratamiento se basa en el consentimiento del usuario (al aceptar esta política y el aviso de cookies/publicidad) y en la ejecución del servicio (al solicitar un cálculo o chat).
                    </p>
                </section>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white">5. Destinatarios (Terceros)</h2>
                    <p>Tus datos pueden ser compartidos con proveedores tecnológicos necesarios para el servicio:</p>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                        <li>
                            <strong className="text-white">Proveedor de IA:</strong> Google Gemini (Solo se envía el texto de la consulta, sin datos identificativos del usuario).
                        </li>
                        <li>
                            <strong className="text-white">Publicidad:</strong> Google Adsense / AdMob. Estos proveedores pueden usar identificadores de dispositivo para personalizar anuncios.
                        </li>
                    </ul>
                </section>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white">6. Conservación de los datos</h2>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                        <li>
                            <strong className="text-white">Datos de Nóminas/Reclamaciones:</strong> Se procesan localmente en el dispositivo y NO se suben a ningún servidor persistente.
                        </li>
                        <li>
                            <strong className="text-white">Historial del Chat:</strong> Se almacena localmente en su dispositivo para su comodidad.
                        </li>
                    </ul>
                </section>

                <section className="space-y-4">
                    <h2 className="text-xl font-bold text-white">7. Derechos del Usuario</h2>
                    <p>
                        Puedes ejercer tus derechos de acceso, rectificación, supresión y oposición enviando un email a soporte_asistentehandling@outlook.es.
                    </p>
                </section >
            </div >
        </div >
    );
}
