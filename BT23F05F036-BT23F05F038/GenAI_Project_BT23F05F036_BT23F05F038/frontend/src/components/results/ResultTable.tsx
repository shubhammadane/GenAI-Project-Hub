import React, { useState, useMemo } from 'react';
import type { ExecutionResult } from '../../types';
import { Download, ChevronLeft, ChevronRight, Search, Clock, FileSpreadsheet } from 'lucide-react';

interface ResultTableProps {
  execution: ExecutionResult;
  queryName?: string;
}

export const ResultTable: React.FC<ResultTableProps> = ({ execution, queryName = 'query_result' }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Filter rows
  const filteredRows = useMemo(() => {
    if (!searchTerm.trim()) return execution.rows;
    const term = searchTerm.toLowerCase();
    return execution.rows.filter((r) =>
      Object.values(r).some((val) => String(val).toLowerCase().includes(term))
    );
  }, [execution.rows, searchTerm]);

  // Pagination calculation
  const totalPages = Math.ceil(filteredRows.length / pageSize) || 1;
  const paginatedRows = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredRows.slice(start, start + pageSize);
  }, [filteredRows, currentPage, pageSize]);

  // Export to CSV
  const handleDownloadCsv = () => {
    if (!execution.columns.length || !execution.rows.length) return;
    const header = execution.columns.join(',');
    const rowsText = execution.rows.map((row) =>
      execution.columns
        .map((col) => {
          const val = row[col];
          if (val === null || val === undefined) return '';
          const str = String(val).replace(/"/g, '""');
          return `"${str}"`;
        })
        .join(',')
    );

    const csvContent = 'data:text/csv;charset=utf-8,' + [header, ...rowsText].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${queryName}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!execution.rows.length) {
    return (
      <div className="p-8 text-center text-slate-400 dark:text-slate-500 bg-slate-50 dark:bg-slate-900/40 rounded-xl border border-slate-200 dark:border-slate-800">
        <FileSpreadsheet className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-xs">No records returned by this query.</p>
      </div>
    );
  }

  return (
    <div className="w-full bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden text-xs">
      {/* Top Controls Bar */}
      <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2" />
            <input
              type="text"
              placeholder="Search result rows..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-8 pr-3 py-1 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 text-xs focus:outline-hidden focus:ring-1 focus:ring-blue-500 w-48"
            />
          </div>

          <div className="flex items-center gap-1 text-[11px] text-slate-500 font-mono">
            <Clock className="w-3 h-3" />
            <span>{execution.execution_time_ms} ms</span>
            <span>•</span>
            <span>{execution.row_count.toLocaleString()} total rows</span>
          </div>
        </div>

        <button
          onClick={handleDownloadCsv}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 text-xs font-medium shadow-xs transition-colors"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export CSV</span>
        </button>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto max-h-80">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-100 dark:bg-slate-800 sticky top-0 z-10 text-slate-700 dark:text-slate-300 font-semibold border-b border-slate-200 dark:border-slate-700 select-none">
            <tr>
              <th className="py-2 px-3 text-[11px] w-12 text-slate-400">#</th>
              {execution.columns.map((col) => (
                <th key={col} className="py-2 px-3 text-[11px] whitespace-nowrap">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {paginatedRows.map((row, idx) => (
              <tr
                key={idx}
                className="hover:bg-blue-50/40 dark:hover:bg-slate-800/40 transition-colors"
              >
                <td className="py-2 px-3 text-slate-400 font-mono text-[11px]">
                  {(currentPage - 1) * pageSize + idx + 1}
                </td>
                {execution.columns.map((col) => {
                  const val = row[col];
                  return (
                    <td
                      key={col}
                      className="py-2 px-3 text-slate-700 dark:text-slate-300 whitespace-nowrap font-mono text-[11px]"
                    >
                      {val === null || val === undefined ? (
                        <span className="text-slate-400 italic">null</span>
                      ) : typeof val === 'number' ? (
                        val.toLocaleString()
                      ) : (
                        String(val)
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
        <div className="flex items-center gap-2">
          <span>Rows per page:</span>
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setCurrentPage(1);
            }}
            className="py-0.5 px-2 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-xs"
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
          <span className="font-mono text-[11px]">
            Showing {(currentPage - 1) * pageSize + 1}-
            {Math.min(currentPage * pageSize, filteredRows.length)} of {filteredRows.length}
          </span>
        </div>

        <div className="flex items-center gap-1">
          <button
            disabled={currentPage <= 1}
            onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
            className="p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-40 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="px-2 font-mono text-[11px]">
            {currentPage} / {totalPages}
          </span>
          <button
            disabled={currentPage >= totalPages}
            onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
            className="p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-40 transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
