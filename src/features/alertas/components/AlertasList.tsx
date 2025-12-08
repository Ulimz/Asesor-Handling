import { useEffect, useState } from "react";

interface Alerta {
  title: string;
  description: string;
  type: string;
  created_at: string;
}

export default function AlertasList() {
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAlertas() {
      setLoading(true);
      try {
        const res = await fetch("/api/alertas");
        const data = await res.json();
        setAlertas(data || []);
      } catch {
        setAlertas([]);
      }
      setLoading(false);
    }
    fetchAlertas();
  }, []);

  return (
    <section className="max-w-2xl mx-auto py-12">
      <h2 className="text-2xl font-bold mb-6 text-yellow-700 dark:text-yellow-300">Alertas legales</h2>
      {loading ? (
        <p className="text-yellow-500">Cargando alertas...</p>
      ) : alertas.length === 0 ? (
        <p className="text-slate-500">No hay alertas legales recientes.</p>
      ) : (
        <ul className="space-y-6">
          {alertas.map((alerta, i) => (
            <li key={i} className="p-6 bg-yellow-50 dark:bg-yellow-900 rounded-xl border border-yellow-200 dark:border-yellow-700 shadow">
              <h3 className="font-bold text-lg text-yellow-900 dark:text-yellow-100 mb-2">{alerta.title}</h3>
              <p className="text-yellow-800 dark:text-yellow-200 mb-2">{alerta.description}</p>
              <span className="text-xs text-yellow-600 dark:text-yellow-300">{alerta.type} · {new Date(alerta.created_at).toLocaleDateString()}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
