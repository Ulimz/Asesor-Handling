import { useState } from "react";

export default function LegalIAChat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setAnswer("");
    try {
      const res = await fetch("/api/ia/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });
      const data = await res.json();
      setAnswer(data.answer || "Sin respuesta");
    } catch {
      setAnswer("Error al consultar la IA");
    }
    setLoading(false);
  };

  return (
    <section className="max-w-2xl mx-auto py-12">
      <h2 className="text-2xl font-bold mb-6 text-slate-800 dark:text-slate-100">Agente IA legal</h2>
      <form onSubmit={handleAsk} className="flex gap-2 mb-8">
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="Ejemplo: ¿Cuántos días de vacaciones tengo?"
          className="flex-1 px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-lg"
          required
        />
        <button type="submit" className="px-6 py-3 rounded-xl bg-slate-800 text-white font-bold shadow hover:bg-slate-900 transition" disabled={loading}>
          {loading ? "Consultando..." : "Preguntar"}
        </button>
      </form>
      {answer && (
        <div className="p-6 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 shadow text-lg text-slate-800 dark:text-slate-100">
          {answer}
        </div>
      )}
    </section>
  );
}
