import React from 'react';
import type { TableProfile } from '../../types';
import { X, Table2 } from 'lucide-react';

interface PreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  profile: TableProfile | null;
}

export const PreviewModal: React.FC<PreviewModalProps> = ({ isOpen, onClose, profile }) => {
  if (!isOpen || !profile) return null;

  const columns = profile.columns.map((c) => c.name);
  const rows = profile.preview_rows;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="w-full max-w-4xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden text-slate-800 dark:text-slate-100 flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
              <Table2 className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-semibold text-sm">Data Preview: {profile.table_name}</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Displaying first 5 rows across {profile.column_count} columns
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Table View */}
        <div className="flex-1 overflow-auto p-4">
          <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th className="py-2 px-3 text-[11px] w-10 text-slate-400">#</th>
                  {columns.map((col) => (
                    <th key={col} className="py-2 px-3 text-[11px] whitespace-nowrap">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px]">
                {rows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <td className="py-2 px-3 text-slate-400">{idx + 1}</td>
                    {columns.map((col) => (
                      <td key={col} className="py-2 px-3 whitespace-nowrap text-slate-700 dark:text-slate-300">
                        {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-slate-400 italic">null</span>}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 bg-slate-50 dark:bg-slate-800/60 border-t border-slate-200 dark:border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-medium bg-slate-200 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
