import DarkModeToggle from "./DarkModeToggle";

export default function MainNavbar() {
  return (
    <nav className="flex items-center justify-between px-6 py-4 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 shadow">
      <div className="flex items-center gap-3">
        <span className="font-extrabold text-xl text-blue-700 dark:text-blue-300">Asistente Handling</span>
      </div>
      <div className="flex items-center gap-4">
        <a href="/features/articulos" className="font-medium text-blue-700 dark:text-blue-300 hover:underline">Artículos</a>
        <a href="/features/calculadoras" className="font-medium text-purple-700 dark:text-purple-300 hover:underline">Calculadoras</a>
        <a href="/features/reclamaciones" className="font-medium text-green-700 dark:text-green-300 hover:underline">Reclamaciones</a>
        <a href="/features/alertas" className="font-medium text-yellow-700 dark:text-yellow-300 hover:underline">Alertas</a>
        <a href="/features/ia" className="font-medium text-slate-800 dark:text-slate-100 hover:underline">IA Legal</a>
        <DarkModeToggle />
      </div>
    </nav>
  );
}
