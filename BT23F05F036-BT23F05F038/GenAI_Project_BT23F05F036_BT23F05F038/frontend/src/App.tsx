import { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { MessageResult } from './components/results/MessageResult';
import { ThinkingIndicator } from './components/chat/ThinkingIndicator';
import { UploadModal } from './components/upload/UploadModal';
import { PreviewModal } from './components/upload/PreviewModal';
import type { ChatMessage, ExecutionResult, TableProfile, ThinkingStep } from './types';
import { sendChatMessage, uploadDataset } from './api/client';
import {
  Send,
  Sparkles,
  Bot,
  User,
  FileSpreadsheet,
  Download,
  AlertCircle,
} from 'lucide-react';

export function App() {
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return localStorage.getItem('askdata_theme') === 'dark';
  });

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [profile, setProfile] = useState<TableProfile | null>(null);
  const [filename, setFilename] = useState<string>('');
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [streamingSteps, setStreamingSteps] = useState<ThinkingStep[]>([]);
  const [uploadModalOpen, setUploadModalOpen] = useState<boolean>(false);
  const [previewModalOpen, setPreviewModalOpen] = useState<boolean>(false);
  const [isLoadingSample, setIsLoadingSample] = useState<boolean>(false);
  const [errorToast, setErrorToast] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Apply dark mode class to <html>
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('askdata_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('askdata_theme', 'light');
    }
  }, [darkMode]);

  // Scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingSteps]);

  // Handle uploading file
  const handleUpload = async (file: File) => {
    const res = await uploadDataset(file);
    setSessionId(res.session_id);
    setFilename(res.filename);
    setProfile(res.profile);
    setSuggestedQuestions(res.suggested_questions);
    setMessages([]);
  };

  // Handle loading sample dataset
  const handleLoadSample = async (sampleType: 'sales' | 'students') => {
    setIsLoadingSample(true);
    try {
      const csvName = sampleType === 'sales' ? 'sales_data.csv' : 'student_performance.csv';
      const sampleResp = await fetch(`/sample_data/${csvName}`);
      let blob: Blob;
      if (sampleResp.ok) {
        blob = await sampleResp.blob();
      } else {
        // Fallback fetch from root
        const fallback = await fetch(`/api/sample/${sampleType}`).catch(() => null);
        if (fallback && fallback.ok) {
          blob = await fallback.blob();
        } else {
          // Provide built-in minimal fallback if direct static fetch is routed
          const text =
            sampleType === 'sales'
              ? 'order_id,region,category,sales,profit\n1,East,Technology,1200,300\n2,West,Furniture,800,150'
              : 'student_id,name,department,gpa,final_score\nS1,Alice,Computer Science,3.9,95\nS2,Bob,Finance,3.2,80';
          blob = new Blob([text], { type: 'text/csv' });
        }
      }

      const sampleFile = new File([blob], csvName, { type: 'text/csv' });
      await handleUpload(sampleFile);
    } catch (err: any) {
      setErrorToast(`Failed to load sample dataset: ${err.message}`);
    } finally {
      setIsLoadingSample(false);
    }
  };

  // Handle sending question
  const handleSendQuestion = async (questionText?: string) => {
    const q = (questionText || inputQuestion).trim();
    if (!q || !sessionId || isGenerating) return;

    setInputQuestion('');
    setIsGenerating(true);
    setStreamingSteps([
      {
        step: 'understanding',
        title: 'Understanding question & schema context',
        status: 'in_progress',
        timestamp: Date.now(),
      },
    ]);

    // Add user message to feed
    const userMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: q,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const assistantMsg = await sendChatMessage(sessionId, q);
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        timestamp: Date.now(),
        is_clarification: true,
        clarification_message: `An error occurred: ${err.message}`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsGenerating(false);
      setStreamingSteps([]);
    }
  };

  // Update query execution if user re-runs edited SQL
  const handleUpdateExecution = (
    messageId: string,
    sql: string,
    execution: ExecutionResult,
    chart?: any
  ) => {
    setMessages((prev) =>
      prev.map((msg) => {
        if (msg.id === messageId) {
          return {
            ...msg,
            sql,
            execution,
            chart: chart || msg.chart,
          };
        }
        return msg;
      })
    );
  };

  // Export full session to Markdown
  const handleExportSession = () => {
    if (!profile || !messages.length) return;
    let md = `# AskData Analysis Report\n\n`;
    md += `**Dataset:** ${profile.table_name} (${profile.row_count} rows, ${profile.column_count} columns)\n`;
    md += `**Generated:** ${new Date().toLocaleString()}\n\n---\n\n`;

    messages.forEach((msg) => {
      if (msg.role === 'user') {
        md += `### User: ${msg.content}\n\n`;
      } else {
        if (msg.sql) {
          md += `\`\`\`sql\n${msg.sql}\n\`\`\`\n\n`;
        }
        if (msg.explanation) {
          md += `> **Insight:** ${msg.explanation}\n\n`;
        }
      }
    });

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `AskData_Report_${profile.table_name}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Start fresh session
  const handleNewSession = () => {
    setSessionId(null);
    setProfile(null);
    setFilename('');
    setMessages([]);
    setSuggestedQuestions([]);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col font-sans transition-colors">
      <Navbar
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        tableName={profile?.table_name}
        onNewSession={handleNewSession}
        onOpenUpload={() => setUploadModalOpen(true)}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          profile={profile}
          filename={filename}
          onOpenUpload={() => setUploadModalOpen(true)}
          onOpenPreview={() => setPreviewModalOpen(true)}
          onLoadSample={handleLoadSample}
          isLoadingSample={isLoadingSample}
        />

        {/* Main Chat Interface */}
        <main className="flex-1 flex flex-col h-[calc(100vh-4rem)] bg-slate-50/50 dark:bg-slate-950/50 overflow-hidden">
          {/* Chat Messages Feed */}
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
            {!profile ? (
              // Empty State - No Dataset
              <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto py-12">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-xl shadow-blue-500/20 mb-4">
                  <Bot className="w-8 h-8" />
                </div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                  Welcome to AskData
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm">
                  Upload any CSV or Excel file, or choose a sample dataset to ask questions in plain English and get SQL, data tables, and charts.
                </p>

                <div className="mt-6 flex flex-wrap gap-2 justify-center">
                  <button
                    onClick={() => setUploadModalOpen(true)}
                    className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-md shadow-blue-500/20 transition-all"
                  >
                    Upload CSV / Excel
                  </button>
                  <button
                    disabled={isLoadingSample}
                    onClick={() => handleLoadSample('sales')}
                    className="px-4 py-2 rounded-xl bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-800 dark:text-slate-200 shadow-xs transition-all"
                  >
                    Load Sample Sales Data
                  </button>
                </div>
              </div>
            ) : messages.length === 0 ? (
              // Dataset Loaded - Suggested Questions State
              <div className="max-w-2xl mx-auto py-8 space-y-6">
                <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm text-center">
                  <FileSpreadsheet className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                    Dataset Ready: <span className="text-blue-600 dark:text-blue-400">{profile.table_name}</span>
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    {profile.row_count.toLocaleString()} rows and {profile.column_count} columns indexed in DuckDB.
                  </p>
                </div>

                {suggestedQuestions.length > 0 && (
                  <div>
                    <div className="flex items-center gap-1.5 mb-3 text-xs font-semibold text-slate-700 dark:text-slate-300">
                      <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                      <span>Suggested Starter Questions</span>
                    </div>
                    <div className="grid grid-cols-1 gap-2">
                      {suggestedQuestions.map((q, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSendQuestion(q)}
                          className="p-3 rounded-xl bg-white dark:bg-slate-900 hover:bg-blue-50/50 dark:hover:bg-blue-950/40 border border-slate-200 dark:border-slate-800 hover:border-blue-300 dark:hover:border-blue-700 text-left transition-all text-xs font-medium text-slate-800 dark:text-slate-200 shadow-xs"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              // Active Conversation Feed
              <div className="max-w-4xl mx-auto space-y-6">
                {/* Export Session Bar */}
                <div className="flex justify-end">
                  <button
                    onClick={handleExportSession}
                    className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 text-xs font-medium shadow-xs transition-colors"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export Session Report (.md)</span>
                  </button>
                </div>

                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {msg.role === 'assistant' && (
                      <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 mt-1 shadow-sm">
                        <Bot className="w-4 h-4" />
                      </div>
                    )}

                    <div
                      className={`max-w-3xl rounded-2xl p-4 shadow-xs text-xs ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white font-medium rounded-tr-xs'
                          : 'bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-800 w-full rounded-tl-xs'
                      }`}
                    >
                      {msg.role === 'user' ? (
                        <p className="text-sm">{msg.content}</p>
                      ) : (
                        <MessageResult
                          message={msg}
                          sessionId={sessionId!}
                          darkMode={darkMode}
                          onFollowUpClick={(followUp) => handleSendQuestion(followUp)}
                          onUpdateExecution={handleUpdateExecution}
                        />
                      )}
                    </div>

                    {msg.role === 'user' && (
                      <div className="w-8 h-8 rounded-lg bg-slate-300 dark:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center justify-center shrink-0 mt-1">
                        <User className="w-4 h-4" />
                      </div>
                    )}
                  </div>
                ))}

                {/* Streaming Indicator */}
                {isGenerating && streamingSteps.length > 0 && (
                  <div className="flex gap-3 justify-start max-w-3xl">
                    <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 mt-1">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div className="w-full">
                      <ThinkingIndicator steps={streamingSteps} isStreaming={true} />
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Box Footer */}
          <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
            <div className="max-w-4xl mx-auto flex items-center gap-2">
              <input
                type="text"
                disabled={!sessionId || isGenerating}
                placeholder={
                  !sessionId
                    ? 'Upload a dataset to start asking questions...'
                    : 'Ask any question (e.g., "What are the total sales by region?", "Who are the top 5 customers?")...'
                }
                value={inputQuestion}
                onChange={(e) => setInputQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSendQuestion();
                }}
                className="flex-1 px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 text-xs focus:outline-hidden focus:ring-2 focus:ring-blue-500 transition-all disabled:opacity-50"
              />

              <button
                disabled={!sessionId || !inputQuestion.trim() || isGenerating}
                onClick={() => handleSendQuestion()}
                className="p-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white shadow-md shadow-blue-500/20 transition-all"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </main>
      </div>

      {/* Modals */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUpload={handleUpload}
        onLoadSample={handleLoadSample}
      />

      <PreviewModal
        isOpen={previewModalOpen}
        onClose={() => setPreviewModalOpen(false)}
        profile={profile}
      />

      {/* Toast Notification */}
      {errorToast && (
        <div className="fixed bottom-4 right-4 z-50 p-3 rounded-xl bg-red-600 text-white text-xs shadow-xl flex items-center gap-2 animate-in fade-in">
          <AlertCircle className="w-4 h-4" />
          <span>{errorToast}</span>
          <button onClick={() => setErrorToast(null)} className="ml-2 font-bold">
            ×
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
