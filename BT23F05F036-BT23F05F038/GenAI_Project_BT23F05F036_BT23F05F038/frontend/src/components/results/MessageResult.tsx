import React, { useState } from 'react';
import type { ChatMessage, ExecutionResult } from '../../types';
import { ThinkingIndicator } from '../chat/ThinkingIndicator';
import { PlotlyChart } from './PlotlyChart';
import { ResultTable } from './ResultTable';
import { SqlEditor } from './SqlEditor';
import {
  BarChart2,
  Table as TableIcon,
  Code2,
  HelpCircle,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';

interface MessageResultProps {
  message: ChatMessage;
  sessionId: string;
  darkMode?: boolean;
  onFollowUpClick: (question: string) => void;
  onUpdateExecution: (messageId: string, sql: string, execution: ExecutionResult, chart?: any) => void;
}

export const MessageResult: React.FC<MessageResultProps> = ({
  message,
  sessionId,
  darkMode = false,
  onFollowUpClick,
  onUpdateExecution,
}) => {
  const hasChart = message.chart && message.chart.chart_type !== 'none';
  const [activeTab, setActiveTab] = useState<'chart' | 'table' | 'sql'>(
    hasChart ? 'chart' : 'table'
  );

  // Clarification state
  if (message.is_clarification) {
    return (
      <div className="space-y-3">
        {message.thinking_steps && message.thinking_steps.length > 0 && (
          <ThinkingIndicator steps={message.thinking_steps} />
        )}
        <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900 text-amber-900 dark:text-amber-200 flex items-start gap-3 text-xs">
          <HelpCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-sm">Need Clarification</p>
            <p className="leading-relaxed">
              {message.clarification_message || message.explanation || 'Could you please clarify your request?'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 w-full">
      {/* Thinking Steps */}
      {message.thinking_steps && message.thinking_steps.length > 0 && (
        <ThinkingIndicator steps={message.thinking_steps} />
      )}

      {/* Tabs Navigator */}
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
        <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-lg text-xs">
          {hasChart && (
            <button
              onClick={() => setActiveTab('chart')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-all ${
                activeTab === 'chart'
                  ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <BarChart2 className="w-3.5 h-3.5" />
              <span>Chart</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded uppercase bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 font-mono">
                {message.chart?.chart_type}
              </span>
            </button>
          )}

          <button
            onClick={() => setActiveTab('table')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-all ${
              activeTab === 'table'
                ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <TableIcon className="w-3.5 h-3.5" />
            <span>Table</span>
            {message.execution && (
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-mono">
                {message.execution.row_count}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('sql')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-all ${
              activeTab === 'sql'
                ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>SQL</span>
          </button>
        </div>
      </div>

      {/* Tab Panels */}
      <div className="w-full">
        {activeTab === 'chart' && message.chart && hasChart && (
          <PlotlyChart chart={message.chart} darkMode={darkMode} />
        )}

        {activeTab === 'table' && message.execution && (
          <ResultTable
            execution={message.execution}
            queryName={message.sql?.slice(0, 30).replace(/[^a-zA-Z0-9]/g, '_') || 'query'}
          />
        )}

        {activeTab === 'sql' && message.sql && (
          <SqlEditor
            initialSql={message.sql}
            sessionId={sessionId}
            onQueryExecuted={(newSql, newExec, newChart) => {
              onUpdateExecution(message.id, newSql, newExec, newChart);
            }}
          />
        )}
      </div>

      {/* Grounded Explanation Card */}
      {message.explanation && (
        <div className="p-3.5 rounded-xl bg-gradient-to-r from-blue-50/50 to-indigo-50/50 dark:from-slate-800/60 dark:to-slate-800/30 border border-blue-100 dark:border-slate-700/60 text-xs text-slate-800 dark:text-slate-200">
          <div className="flex items-center gap-1.5 mb-1 text-blue-700 dark:text-blue-400 font-semibold text-[11px] uppercase tracking-wider">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>Key Takeaways & Insight</span>
          </div>
          <p className="leading-relaxed text-slate-700 dark:text-slate-300">
            {message.explanation}
          </p>
        </div>
      )}

      {/* Suggested Follow-ups */}
      {message.follow_up_questions && message.follow_up_questions.length > 0 && (
        <div className="pt-1">
          <span className="text-[11px] font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider block mb-1.5">
            Suggested Follow-up Questions
          </span>
          <div className="flex flex-wrap gap-1.5">
            {message.follow_up_questions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => onFollowUpClick(q)}
                className="group flex items-center gap-1 px-2.5 py-1 rounded-full text-xs bg-slate-100 dark:bg-slate-800 hover:bg-blue-50 dark:hover:bg-blue-950/60 border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-700 text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-300 transition-all text-left"
              >
                <span>{q}</span>
                <ArrowRight className="w-3 h-3 opacity-0 -ml-1 group-hover:opacity-100 group-hover:ml-0 transition-all" />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
