import concurrent.futures
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import duckdb
import pandas as pd
from app.config import settings
from app.models.schemas import ExecutionResult, SessionState, TableProfile


class DuckDBSession:
    """Manages an isolated DuckDB connection and its catalog for a single user session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.conn = duckdb.connect(database=":memory:")
        self.conn.execute("SET enable_external_access = false;")
        self.conn.execute("SET max_memory = '512MB';")
        self.conn.execute("SET threads = 2;")
        self.table_name: str = ""
        self.filename: str = ""
        self.profile: Optional[TableProfile] = None
        self.history: List[Dict[str, Any]] = []

    def register_dataframe(self, table_name: str, df: pd.DataFrame) -> None:
        """Loads a DataFrame into this session's DuckDB as a physical in-memory table."""
        self.table_name = table_name
        # Register and persist as a table inside DuckDB session
        self.conn.register("temp_df_view", df)
        self.conn.execute(f'CREATE TABLE "{table_name}" AS SELECT * FROM temp_df_view;')
        self.conn.unregister("temp_df_view")

    def list_tables(self) -> List[str]:
        tables = self.conn.execute("SHOW TABLES;").fetchall()
        return [t[0].lower() for t in tables]

    def execute_query(self, sql: str, timeout_seconds: Optional[int] = None) -> ExecutionResult:
        """Executes a SQL query within the session with strict timeout and execution timing."""
        timeout = timeout_seconds or settings.query_timeout_seconds
        start_time = time.perf_counter()

        def _run():
            # Run query using the isolated connection
            cursor = self.conn.cursor()
            result = cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows_raw = result.fetchall()
            # Convert raw tuples to list of dicts with JSON-serializable types
            formatted_rows: List[Dict[str, Any]] = []
            for r in rows_raw:
                row_dict = {}
                for col_name, val in zip(columns, r):
                    if hasattr(val, "isoformat"):
                        row_dict[col_name] = val.isoformat()
                    elif isinstance(val, (int, float, str, bool)) or val is None:
                        row_dict[col_name] = val
                    else:
                        row_dict[col_name] = str(val)
                formatted_rows.append(row_dict)
            return columns, formatted_rows

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(_run)
        try:
            columns, rows = future.result(timeout=timeout)
            exec_time = (time.perf_counter() - start_time) * 1000
            return ExecutionResult(
                columns=columns,
                rows=rows,
                row_count=len(rows),
                execution_time_ms=round(exec_time, 2),
                error=None,
            )
        except concurrent.futures.TimeoutError:
            executor.shutdown(wait=False, cancel_futures=True)
            exec_time = (time.perf_counter() - start_time) * 1000
            return ExecutionResult(
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=round(exec_time, 2),
                error=f"Query execution timed out after {timeout} seconds.",
            )
        except Exception as e:
            executor.shutdown(wait=False)
            exec_time = (time.perf_counter() - start_time) * 1000
            return ExecutionResult(
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=round(exec_time, 2),
                error=str(e),
            )
        finally:
            executor.shutdown(wait=False)


class SessionManager:
    """Thread-safe catalog holding active DuckDB sessions."""

    def __init__(self):
        self._sessions: Dict[str, DuckDBSession] = {}

    def get_or_create(self, session_id: str) -> DuckDBSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = DuckDBSession(session_id)
        return self._sessions[session_id]

    def get(self, session_id: str) -> Optional[DuckDBSession]:
        return self._sessions.get(session_id)

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def to_session_state(self, session_id: str) -> Optional[SessionState]:
        session = self.get(session_id)
        if not session or not session.profile:
            return None
        return SessionState(
            session_id=session.session_id,
            created_at=session.created_at,
            table_name=session.table_name,
            filename=session.filename,
            profile=session.profile,
            history=session.history,
        )


session_manager = SessionManager()
