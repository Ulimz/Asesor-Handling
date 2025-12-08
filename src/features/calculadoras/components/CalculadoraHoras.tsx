import { useState } from "react";

export default function CalculadoraHoras() {
  const [horasBase, setHorasBase] = useState(0);
  const [horasExtra, setHorasExtra] = useState(0);
  const total = horasBase + horasExtra;

  return (
    <section className="max-w-md mx-auto py-12">
      <h2 className="text-2xl font-bold mb-6 text-purple-700 dark:text-purple-300">Calculadora de horas complementarias</h2>
      <form className="space-y-4">
        <div>
          <label className="block mb-1 font-medium">Horas base</label>
          <input type="number" value={horasBase} onChange={e => setHorasBase(Number(e.target.value))} className="w-full px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700" min={0} />
        </div>
        <div>
          <label className="block mb-1 font-medium">Horas extra</label>
          <input type="number" value={horasExtra} onChange={e => setHorasExtra(Number(e.target.value))} className="w-full px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700" min={0} />
        </div>
      </form>
      <div className="mt-6 text-lg font-bold text-purple-700 dark:text-purple-300">Total horas: {total}</div>
    </section>
  );
}
