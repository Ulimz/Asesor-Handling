import { useState } from "react";

export default function ReclamacionForm() {
  const [tipo, setTipo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [enviado, setEnviado] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Aquí iría la llamada al backend
    setEnviado(true);
  };

  return (
    <section className="max-w-md mx-auto py-12">
      <h2 className="text-2xl font-bold mb-6 text-green-700 dark:text-green-300">Generar reclamación personalizada</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1 font-medium">Tipo de reclamación</label>
          <input type="text" value={tipo} onChange={e => setTipo(e.target.value)} className="w-full px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700" required />
        </div>
        <div>
          <label className="block mb-1 font-medium">Descripción</label>
          <textarea value={descripcion} onChange={e => setDescripcion(e.target.value)} className="w-full px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700" required />
        </div>
        <button type="submit" className="px-6 py-3 rounded-xl bg-green-600 text-white font-bold shadow hover:bg-green-700 transition">Enviar reclamación</button>
      </form>
      {enviado && <div className="mt-6 text-lg font-bold text-green-700 dark:text-green-300">¡Reclamación enviada!</div>}
    </section>
  );
}
