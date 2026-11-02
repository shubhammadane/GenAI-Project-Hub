import type { ChatMessage, ExecutionResult, SessionState, UploadResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function uploadDataset(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(errorData.detail || 'Upload failed');
  }

  return res.json();
}

export async function sendChatMessage(sessionId: string, question: string): Promise<ChatMessage> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Query failed' }));
    throw new Error(err.detail || 'Query failed');
  }

  const data = await res.json();
  return {
    id: `msg-${Date.now()}`,
    role: 'assistant',
    timestamp: Date.now(),
    sql: data.sql,
    execution: data.execution,
    chart: data.chart,
    explanation: data.explanation,
    follow_up_questions: data.follow_up_questions,
    thinking_steps: data.thinking_steps,
    is_clarification: data.is_clarification,
    clarification_message: data.clarification_message,
  };
}

export async function executeCustomSql(
  sessionId: string,
  sql: string
): Promise<{ sql: string; execution: ExecutionResult; chart?: any; is_valid: boolean; error?: string }> {
  const res = await fetch(`${API_BASE}/api/run-sql`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, sql }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Execution failed' }));
    throw new Error(err.detail || 'Execution failed');
  }

  return res.json();
}

export async function fetchSession(sessionId: string): Promise<SessionState> {
  const res = await fetch(`${API_BASE}/api/session/${sessionId}`);
  if (!res.ok) throw new Error('Session not found');
  return res.json();
}
