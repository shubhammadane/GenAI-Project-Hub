import React, { useState } from 'react';
import { Play, Copy, Check, AlertCircle, Terminal } from 'lucide-react';
import { executeCustomSql } from '../../api/client';
import type { ExecutionResult } from '../../types';

interface SqlEditorProps {
  initialSql: string;
  sessionId: string;
  onQueryExecuted: (sql: string, execution: ExecutionResult, chart?: any) => void;
}

export const SqlEditor: React.FC<SqlEditorProps> = ({
  initialSql,
  sessionId,
  onQueryExecuted,
}) => {
  const [sql, setSql] = useState(initialSql);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleRun = async () => {
    if (!sql.trim()) return;
    setIsRunning(true);
    setError(null);
    try {
      const res = await executeCustomSql(sessionId, sql);
      if (!res.is_valid || res.error) {
        setError(res.error || 'Query validation failed');
      } else {
        onQueryExecuted(res.sql, res.execution, res.chart);
      }
    } catch (err: any) {
      setError(err.message || 'Execution failed');
    } finally {
      setIsRunning(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-900 text-slate-100 overflow-hidden text-xs shadow-inner">
      {/* Top Header */}
      <div className="px-3 py-2 bg-slate-800/80 border-b border-slate-700/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-blue-400" />
          <span className="font-mono font-medium text-slate-300 text-[11px]">
            DuckDB SQL Editor (Read-Only)
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-1 rounded bg-slate-700/60 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors text-[11px]"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
          <button
            onClick={handleRun}
            disabled={isRunning}
            className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium transition-colors shadow-sm text-[11px]"
          >
            <Play className={`w-3 h-3 ${isRunning ? 'animate-spin' : ''}`} />
            <span>{isRunning ? 'Running...' : 'Run Query'}</span>
          </button>
        </div>
      </div>

      {/* Code Textarea */}
      <div className="p-3">
        <textarea
          value={sql}
          onChange={(e) => setSql(e.target.value)}
          rows={Math.min(Math.max(sql.split('\n').length + 1, 3), 10)}
          className="w-full bg-transparent font-mono text-[12px] leading-relaxed text-blue-200 focus:outline-hidden resize-y select-text"
          placeholder="SELECT ... FROM ...;"
          spellCheck={false}
        />
      </div>

      {/* Error banner */}
      {error && (
        <div className="px-3 py-2 bg-red-950/80 border-t border-red-800/80 text-red-300 flex items-start gap-2 text-[11px]">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <div className="font-mono break-all">{error}</div>
        </div>
      )}
    </div>
  );
};
