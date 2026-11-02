import React, { useState } from 'react';
import type { ThinkingStep } from '../../types';
import { CheckCircle2, Loader2, AlertCircle, ChevronDown, ChevronUp, Cpu } from 'lucide-react';

interface ThinkingIndicatorProps {
  steps: ThinkingStep[];
  isStreaming?: boolean;
}

export const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({ steps, isStreaming }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!steps || steps.length === 0) return null;

  // Find active step or the latest completed step
  const activeStep = steps.find((s) => s.status === 'in_progress') || steps[steps.length - 1];

  return (
    <div className="my-2 rounded-xl border border-blue-200 dark:border-blue-900/60 bg-blue-50/60 dark:bg-blue-950/30 overflow-hidden text-xs">
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="px-3.5 py-2 flex items-center justify-between cursor-pointer hover:bg-blue-100/50 dark:hover:bg-blue-900/40 transition-colors"
      >
        <div className="flex items-center gap-2">
          {isStreaming ? (
            <Loader2 className="w-4 h-4 text-blue-600 dark:text-blue-400 animate-spin" />
          ) : (
            <Cpu className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          )}
          <span className="font-medium text-slate-800 dark:text-slate-200">
            {isStreaming ? 'Thinking...' : 'Reasoning Process'}
          </span>
          <span className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">
            ({steps.filter((s) => s.status === 'completed').length}/{steps.length} steps)
          </span>
          {activeStep && isStreaming && (
            <span className="ml-2 text-[11px] font-medium text-blue-700 dark:text-blue-300 animate-pulse">
              {activeStep.title}
            </span>
          )}
        </div>

        <button className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {isExpanded && (
        <div className="px-4 py-2.5 border-t border-blue-200/80 dark:border-blue-900/50 space-y-2">
          {steps.map((s, idx) => (
            <div key={idx} className="flex items-start gap-2.5">
              <div className="mt-0.5">
                {s.status === 'completed' && (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                )}
                {s.status === 'in_progress' && (
                  <Loader2 className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400 animate-spin" />
                )}
                {s.status === 'error' && (
                  <AlertCircle className="w-3.5 h-3.5 text-red-500 dark:text-red-400" />
                )}
                {s.status === 'pending' && (
                  <div className="w-3.5 h-3.5 rounded-full border border-slate-300 dark:border-slate-600" />
                )}
              </div>
              <div className="flex-1">
                <p className="font-medium text-slate-800 dark:text-slate-200">{s.title}</p>
                {s.detail && (
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 font-mono break-all mt-0.5">
                    {s.detail}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
