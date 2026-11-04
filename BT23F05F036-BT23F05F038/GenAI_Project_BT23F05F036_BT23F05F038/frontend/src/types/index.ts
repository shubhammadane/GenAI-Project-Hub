export interface ColumnProfile {
  name: string;
  data_type: string;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  sample_values: any[];
  min_value?: any;
  max_value?: any;
}

export interface TableProfile {
  table_name: string;
  row_count: number;
  column_count: number;
  columns: ColumnProfile[];
  preview_rows: Record<string, any>[];
}

export interface UploadResponse {
  session_id: string;
  filename: string;
  table_name: string;
  profile: TableProfile;
  suggested_questions: string[];
}

export interface ExecutionResult {
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  execution_time_ms: number;
  error?: string | null;
  truncated: boolean;
}

export interface ChartSpec {
  chart_type: string;
  title: string;
  x_axis?: string | null;
  y_axis?: string | string[] | null;
  category_col?: string | null;
  plotly_json: {
    data?: any[];
    layout?: Record<string, any>;
  };
}

export interface ThinkingStep {
  step: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  detail?: string | null;
  timestamp: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content?: string;
  timestamp: number;
  sql?: string | null;
  execution?: ExecutionResult | null;
  chart?: ChartSpec | null;
  explanation?: string | null;
  follow_up_questions?: string[];
  thinking_steps?: ThinkingStep[];
  is_clarification?: boolean;
  clarification_message?: string | null;
}

export interface SessionState {
  session_id: string;
  created_at: string;
  table_name: string;
  filename: string;
  profile: TableProfile;
  history: any[];
}
