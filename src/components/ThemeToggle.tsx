"use client";

import { useTheme } from "../context/ThemeContext";
import { Sun, Moon } from "lucide-react";

export default function ThemeToggle() {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className={`
        p-2 rounded-full transition-all duration-300
        ${theme === 'dark'
                    ? 'bg-slate-800 text-yellow-400 hover:bg-slate-700 hover:text-yellow-300'
                    : 'bg-slate-200 text-slate-900 hover:bg-slate-300'
                }
        focus:outline-none focus:ring-2 focus:ring-brand-cyan
      `}
            aria-label="Toggle Theme"
        >
            {theme === 'dark' ? (
                <Moon className="w-5 h-5" />
            ) : (
                <Sun className="w-5 h-5 text-orange-500" />
            )}
        </button>
    );
}
