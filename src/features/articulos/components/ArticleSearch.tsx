import { useState } from "react";
import { API_URL } from "@/config/api";

interface ArticleResult {
  _source: {
    title: string;
    content: string;
    convenio_id: string;
  };
}

export default function ArticleSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ArticleResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResults([]);
    try {
      const res = await fetch(`${API_URL}/api/articulos/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      setResults(data.results || []);
    } catch {
      setResults([]);
    }
    setLoading(false);
  };

  return (
    <section className="max-w-2xl mx-auto py-12">
      <h2 className="text-2xl font-bold mb-6 text-blue-700 dark:text-blue-300">Buscador semántico de artículos</h2>
      <form onSubmit={handleSearch} className="flex gap-2 mb-8">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ejemplo: descanso nocturno, horas extra, vacaciones..."
          className="flex-1 px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-lg"
          required
        />
        <button type="submit" className="px-6 py-3 rounded-xl bg-blue-600 text-white font-bold shadow hover:bg-blue-700 transition" disabled={loading}>
          {loading ? "Buscando..." : "Buscar"}
        </button>
      </form>
      <div className="space-y-6">
        {results.length === 0 && !loading && <p className="text-slate-500">No hay resultados.</p>}
        {results.map((item, i) => (
          <div key={i} className="p-6 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 shadow">
            <h3 className="font-bold text-lg text-blue-700 dark:text-blue-300 mb-2">{item._source.title}</h3>
            <p className="text-slate-700 dark:text-slate-200 mb-2">{item._source.content}</p>
            <span className="text-xs text-slate-400">Convenio: {item._source.convenio_id}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
