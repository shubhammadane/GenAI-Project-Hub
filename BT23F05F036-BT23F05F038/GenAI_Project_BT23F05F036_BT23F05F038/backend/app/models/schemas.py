from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ColumnProfile(BaseModel):
    name: str
    data_type: str
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: List[Any] = Field(default_factory=list)
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None


class TableProfile(BaseModel):
    table_name: str
    row_count: int
    column_count: int
    columns: List[ColumnProfile]
    preview_rows: List[Dict[str, Any]] = Field(default_factory=list)


class UploadResponse(BaseModel):
    session_id: str
    filename: str
    table_name: str
    profile: TableProfile
    suggested_questions: List[str] = Field(default_factory=list)


class SqlValidationResult(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    sanitized_sql: Optional[str] = None
    referenced_tables: List[str] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    columns: List[str] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    truncated: bool = False


class ChartSpec(BaseModel):
    chart_type: str  # "bar", "line", "pie", "scatter", "histogram", "heatmap", "none"
    title: str
    x_axis: Optional[str] = None
    y_axis: Optional[Union[str, List[str]]] = None
    category_col: Optional[str] = None
    plotly_json: Dict[str, Any] = Field(default_factory=dict)


class ThinkingStep(BaseModel):
    step: str
    title: str
    status: str  # "pending", "in_progress", "completed", "error"
    detail: Optional[str] = None
    timestamp: float = 0.0


class ChatRequest(BaseModel):
    session_id: str
    question: str


class ChatResponse(BaseModel):
    question: str
    sql: Optional[str] = None
    execution: Optional[ExecutionResult] = None
    chart: Optional[ChartSpec] = None
    explanation: Optional[str] = None
    follow_up_questions: List[str] = Field(default_factory=list)
    thinking_steps: List[ThinkingStep] = Field(default_factory=list)
    is_clarification: bool = False
    clarification_message: Optional[str] = None


class RunSqlRequest(BaseModel):
    session_id: str
    sql: str


class RunSqlResponse(BaseModel):
    sql: str
    execution: ExecutionResult
    chart: Optional[ChartSpec] = None
    is_valid: bool = True
    error: Optional[str] = None


class SessionState(BaseModel):
    session_id: str
    created_at: str
    table_name: str
    filename: str
    profile: TableProfile
    history: List[Dict[str, Any]] = Field(default_factory=list)
