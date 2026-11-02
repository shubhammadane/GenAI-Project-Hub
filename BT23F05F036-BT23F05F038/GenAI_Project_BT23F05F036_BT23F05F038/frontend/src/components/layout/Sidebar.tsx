import React, { useState } from 'react';
import type { TableProfile } from '../../types';
import {
  Table2,
  Columns,
  Hash,
  ChevronDown,
  ChevronRight,
  Eye,
  FileSpreadsheet,
  Layers,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  profile: TableProfile | null;
  filename?: string;
  onOpenUpload: () => void;
  onOpenPreview: () => void;
  onLoadSample: (sampleType: 'sales' | 'students') => void;
  isLoadingSample: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  profile,
  filename,
  onOpenUpload,
  onOpenPreview,
  onLoadSample,
  isLoadingSample,
}) => {
  const [expandedCol, setExpandedCol] = useState<string | null>(null);

  const toggleCol = (name: string) => {
    setExpandedCol(expandedCol === name ? null : name);
  };

  const getTypeColor = (dtype: string) => {
    switch (dtype) {
      case 'BIGINT':
      case 'DOUBLE':
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
      case 'TIMESTAMP':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300 border-purple-200 dark:border-purple-800';
      case 'BOOLEAN':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800';
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border-blue-200 dark:border-blue-800';
    }
  };

  return (
    <aside className="w-80 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col h-[calc(100vh-4rem)] select-none">
      {/* Dataset Header / Upload Section */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Table2 className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
              Data Catalog
            </h2>
          </div>
          <button
            onClick={onOpenUpload}
            className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
          >
            Change
          </button>
        </div>

        {profile ? (
          <div className="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-3 border border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-2 mb-2">
              <FileSpreadsheet className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <div className="truncate">
                <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">
                  {profile.table_name}
                </p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
                  {filename || 'in-memory table'}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                <Hash className="w-3.5 h-3.5 text-slate-400" />
                <span>{profile.row_count.toLocaleString()} rows</span>
              </div>
              <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                <Columns className="w-3.5 h-3.5 text-slate-400" />
                <span>{profile.column_count} columns</span>
              </div>
            </div>

            <button
              onClick={onOpenPreview}
              className="mt-2.5 w-full py-1.5 px-3 rounded-lg bg-white dark:bg-slate-700 hover:bg-slate-100 dark:hover:bg-slate-600 border border-slate-200 dark:border-slate-600 text-xs font-medium text-slate-700 dark:text-slate-200 flex items-center justify-center gap-1.5 transition-colors"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Preview 5 Rows</span>
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-center py-4 px-2 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/30">
              <Layers className="w-6 h-6 text-slate-400 mx-auto mb-1.5" />
              <p className="text-xs font-medium text-slate-700 dark:text-slate-300">No Dataset Loaded</p>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                Upload a CSV/Excel file or choose a sample dataset below
              </p>
              <button
                onClick={onOpenUpload}
                className="mt-3 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium transition-colors shadow-sm"
              >
                Upload File
              </button>
            </div>

            <div className="pt-2">
              <span className="text-[11px] font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider block mb-2">
                Quick Sample Datasets
              </span>
              <div className="flex flex-col gap-1.5">
                <button
                  disabled={isLoadingSample}
                  onClick={() => onLoadSample('sales')}
                  className="flex items-center justify-between p-2 rounded-lg text-xs bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 transition-colors text-left"
                >
                  <span className="flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                    <span>Retail Sales Orders</span>
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">CSV • 50 rows</span>
                </button>
                <button
                  disabled={isLoadingSample}
                  onClick={() => onLoadSample('students')}
                  className="flex items-center justify-between p-2 rounded-lg text-xs bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 transition-colors text-left"
                >
                  <span className="flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-blue-500" />
                    <span>Student Performance</span>
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">CSV • 50 rows</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Schema / Columns List */}
      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2.5">
          Columns & Profile {profile && `(${profile.columns.length})`}
        </h3>

        {!profile ? (
          <p className="text-xs text-slate-400 dark:text-slate-600 italic">
            Column data types and distributions will appear once a dataset is loaded.
          </p>
        ) : (
          <div className="space-y-1.5">
            {profile.columns.map((col) => {
              const isExpanded = expandedCol === col.name;
              return (
                <div
                  key={col.name}
                  className="rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden bg-white dark:bg-slate-900/60"
                >
                  <button
                    onClick={() => toggleCol(col.name)}
                    className="w-full px-2.5 py-2 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                  >
                    <div className="flex items-center gap-1.5 truncate">
                      {isExpanded ? (
                        <ChevronDown className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      ) : (
                        <ChevronRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      )}
                      <span className="text-xs font-medium text-slate-800 dark:text-slate-200 truncate">
                        {col.name}
                      </span>
                    </div>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded border font-mono font-medium ${getTypeColor(
                        col.data_type
                      )}`}
                    >
                      {col.data_type}
                    </span>
                  </button>

                  {isExpanded && (
                    <div className="p-2.5 bg-slate-50 dark:bg-slate-800/40 border-t border-slate-200 dark:border-slate-800 text-[11px] space-y-1.5">
                      <div className="flex justify-between text-slate-600 dark:text-slate-400">
                        <span>Null values:</span>
                        <span className="font-mono">
                          {col.null_count} ({col.null_percentage}%)
                        </span>
                      </div>
                      <div className="flex justify-between text-slate-600 dark:text-slate-400">
                        <span>Distinct count:</span>
                        <span className="font-mono">{col.unique_count}</span>
                      </div>
                      {col.min_value !== null && col.max_value !== null && (
                        <div className="flex justify-between text-slate-600 dark:text-slate-400">
                          <span>Range:</span>
                          <span className="font-mono truncate max-w-[120px]">
                            [{col.min_value} to {col.max_value}]
                          </span>
                        </div>
                      )}
                      {col.sample_values && col.sample_values.length > 0 && (
                        <div className="pt-1">
                          <span className="text-slate-500 block mb-1">Sample values:</span>
                          <div className="flex flex-wrap gap-1">
                            {col.sample_values.slice(0, 5).map((val, idx) => (
                              <span
                                key={idx}
                                className="px-1.5 py-0.5 rounded bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-[10px] font-mono text-slate-700 dark:text-slate-300"
                              >
                                {String(val)}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </aside>
  );
};
