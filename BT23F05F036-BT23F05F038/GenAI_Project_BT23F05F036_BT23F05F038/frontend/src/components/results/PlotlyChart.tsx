import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import type { ChartSpec } from '../../types';
import { Download } from 'lucide-react';

interface PlotlyChartProps {
  chart: ChartSpec;
  darkMode?: boolean;
}

export const PlotlyChart: React.FC<PlotlyChartProps> = ({ chart, darkMode = false }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !chart.plotly_json || !chart.plotly_json.data) return;

    const data = chart.plotly_json.data;
    const layout = {
      ...chart.plotly_json.layout,
      autosize: true,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: {
        family: 'Inter, system-ui, sans-serif',
        color: darkMode ? '#e2e8f0' : '#1e293b',
      },
      xaxis: {
        ...(chart.plotly_json.layout?.xaxis || {}),
        gridcolor: darkMode ? '#334155' : '#e2e8f0',
        tickfont: { color: darkMode ? '#94a3b8' : '#64748b' },
      },
      yaxis: {
        ...(chart.plotly_json.layout?.yaxis || {}),
        gridcolor: darkMode ? '#334155' : '#e2e8f0',
        tickfont: { color: darkMode ? '#94a3b8' : '#64748b' },
      },
    };

    const config = {
      responsive: true,
      displayModeBar: false, // We provide custom export buttons
    };

    Plotly.newPlot(containerRef.current, data, layout, config);

    const handleResize = () => {
      if (containerRef.current) {
        Plotly.Plots.resize(containerRef.current);
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (containerRef.current) {
        Plotly.purge(containerRef.current);
      }
    };
  }, [chart, darkMode]);

  const handleDownloadImage = () => {
    if (containerRef.current) {
      Plotly.downloadImage(containerRef.current, {
        format: 'png',
        width: 1000,
        height: 600,
        filename: `${chart.title.toLowerCase().replace(/\s+/g, '_')}_chart`,
      });
    }
  };

  return (
    <div className="relative group w-full bg-slate-50 dark:bg-slate-900/40 rounded-xl p-3 border border-slate-200 dark:border-slate-800">
      <div className="flex items-center justify-between mb-2 px-1">
        <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
          {chart.title}
        </span>
        <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleDownloadImage}
            title="Download Chart as PNG"
            className="flex items-center gap-1 px-2 py-1 rounded bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-[11px] font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 shadow-xs transition-colors"
          >
            <Download className="w-3 h-3" />
            <span>Export PNG</span>
          </button>
        </div>
      </div>
      <div ref={containerRef} className="w-full h-80 min-h-[320px]" />
    </div>
  );
};
