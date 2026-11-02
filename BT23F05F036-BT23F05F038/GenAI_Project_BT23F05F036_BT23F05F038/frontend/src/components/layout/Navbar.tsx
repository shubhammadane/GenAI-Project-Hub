import React from 'react';
import { Database, Moon, Sun, Sparkles, RefreshCw, BarChart3 } from 'lucide-react';

interface NavbarProps {
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
  tableName?: string;
  onNewSession: () => void;
  onOpenUpload: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  darkMode,
  setDarkMode,
  tableName,
  onNewSession,
  onOpenUpload,
}) => {
  return (
    <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30 transition-colors">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
          <BarChart3 className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg tracking-tight text-slate-900 dark:text-white">
              AskData
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full font-semibold bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300">
              AI Analyst
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Natural language text-to-SQL & interactive analytics
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {tableName && (
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs">
            <Database className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
            <span className="font-medium text-slate-700 dark:text-slate-300">
              Active: <span className="font-mono text-blue-600 dark:text-blue-400">{tableName}</span>
            </span>
          </div>
        )}

        <button
          onClick={onOpenUpload}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition-all"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Upload Dataset</span>
        </button>

        <button
          onClick={onNewSession}
          title="Start New Session"
          className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-800 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        <button
          onClick={() => setDarkMode(!darkMode)}
          title="Toggle Theme"
          className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-800 transition-colors"
        >
          {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>
      </div>
    </header>
  );
};
