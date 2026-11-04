import time
from typing import Any, Callable, Dict, List, Optional
from app.config import settings
from app.core.engine import session_manager
from app.core.validator import SqlValidator
from app.models.schemas import (
    ChartSpec,
    ChatResponse,
    ExecutionResult,
    ThinkingStep,
)
from app.services.chart_generator import ChartGenerator
from app.services.context_builder import build_schema_prompt_context
from app.services.explainer import Explainer
from app.services.llm_provider import get_llm_client


class SqlAgent:
    """
    Coordinates the multi-stage Text-to-SQL pipeline with security validation,
    error-correction retry loops, dynamic charting, and grounded explanation.
    Supports real-time progress callbacks for SSE streaming.
    """

    MAX_RETRIES = 2

    @classmethod
    def process_question(
        cls,
        session_id: str,
        question: str,
        progress_callback: Optional[Callable[[ThinkingStep], None]] = None,
    ) -> ChatResponse:
        session = session_manager.get(session_id)
        if not session or not session.profile:
            return ChatResponse(
                question=question,
                is_clarification=True,
                clarification_message="Session not found or no dataset has been uploaded yet. Please upload a CSV/Excel file first.",
            )

        thinking_steps: List[ThinkingStep] = []

        def add_step(step_id: str, title: str, status: str = "in_progress", detail: Optional[str] = None):
            step = ThinkingStep(
                step=step_id,
                title=title,
                status=status,
                detail=detail,
                timestamp=time.time(),
            )
            thinking_steps.append(step)
            if progress_callback:
                progress_callback(step)

        def update_last_step(status: str, detail: Optional[str] = None):
            if thinking_steps:
                thinking_steps[-1].status = status
                if detail:
                    thinking_steps[-1].detail = detail
                if progress_callback:
                    progress_callback(thinking_steps[-1])

        # Step 1: Understanding context
        add_step("understanding", "Analyzing schema and question context")
        llm = get_llm_client()
        schema_context = build_schema_prompt_context(
            profile=session.profile,
            conversation_history=session.history,
        )
        allowed_tables = session.list_tables()
        update_last_step(
            "completed",
            f"Schema loaded: table '{session.table_name}' with {session.profile.column_count} columns and {session.profile.row_count} rows.",
        )

        # Step 2: Text-to-SQL with error self-correction retry loop
        add_step("generating_sql", "Generating SQL query via LLM")
        error_feedback: Optional[str] = None
        sql_candidate = ""
        sanitized_sql = ""
        exec_result: Optional[ExecutionResult] = None

        for attempt in range(cls.MAX_RETRIES + 1):
            llm_result = llm.generate_sql(
                schema_context=schema_context,
                user_question=question,
                error_feedback=error_feedback,
            )

            if llm_result.get("is_clarification"):
                clarification_msg = llm_result.get(
                    "clarification_message",
                    "Could you please clarify your question? Some referenced metrics or columns were not found.",
                )
                update_last_step("completed", "Ambiguity detected. Prompting user for clarification.")
                return ChatResponse(
                    question=question,
                    thinking_steps=thinking_steps,
                    is_clarification=True,
                    clarification_message=clarification_msg,
                )

            sql_candidate = llm_result.get("sql", "").strip()
            update_last_step("completed", f"Generated SQL query: {sql_candidate}")

            # Step 3: AST Validation
            add_step("validating_sql", f"Validating query security & rules (Attempt {attempt + 1})")
            validation = SqlValidator.validate_and_sanitize(
                sql=sql_candidate,
                allowed_tables=allowed_tables,
                default_limit=settings.default_row_limit,
                max_limit=settings.max_row_limit,
            )

            if not validation.is_valid:
                update_last_step("error", f"Security violation: {validation.error_message}")
                error_feedback = f"SQL rejected by security validator: {validation.error_message}"
                if attempt < cls.MAX_RETRIES:
                    add_step("generating_sql", f"Self-correcting SQL generation (Retry {attempt + 1})")
                    continue
                else:
                    return ChatResponse(
                        question=question,
                        sql=sql_candidate,
                        thinking_steps=thinking_steps,
                        is_clarification=True,
                        clarification_message=f"I couldn't safely run that query: {validation.error_message}",
                    )

            sanitized_sql = validation.sanitized_sql or sql_candidate
            update_last_step("completed", "Query validated: strictly read-only SELECT with enforced limits.")

            # Step 4: Execute query
            add_step("executing_sql", "Executing query in isolated DuckDB instance")
            exec_result = session.execute_query(sanitized_sql)

            if exec_result.error:
                update_last_step("error", f"DuckDB execution error: {exec_result.error}")
                error_feedback = f"DuckDB execution error: {exec_result.error}"
                if attempt < cls.MAX_RETRIES:
                    add_step("generating_sql", f"Self-correcting SQL syntax (Retry {attempt + 1})")
                    continue
                else:
                    return ChatResponse(
                        question=question,
                        sql=sanitized_sql,
                        execution=exec_result,
                        thinking_steps=thinking_steps,
                        is_clarification=False,
                        explanation=f"Execution error: {exec_result.error}",
                    )

            update_last_step("completed", f"Query executed successfully: returned {exec_result.row_count} rows in {exec_result.execution_time_ms} ms.")
            break

        # Step 5: Charting via ChartGenerator
        add_step("charting", "Selecting chart type and building Plotly spec")
        chart_spec = ChartGenerator.generate(
            question=question,
            columns=exec_result.columns if exec_result else [],
            rows=exec_result.rows if exec_result else [],
        )
        update_last_step("completed", f"Visualization created: {chart_spec.chart_type} chart.")

        # Step 6: Grounded explanation via Explainer
        add_step("explaining", "Synthesizing grounded natural language explanation")
        explanation = Explainer.explain(
            question=question,
            sql=sanitized_sql,
            columns=exec_result.columns if exec_result else [],
            rows=exec_result.rows if exec_result else [],
            row_count=exec_result.row_count if exec_result else 0,
        )
        update_last_step("completed", "Explanation completed and verified against result rows.")

        # Save to session history for conversational memory
        session.history.append({
            "question": question,
            "sql": sanitized_sql,
            "explanation": explanation,
            "timestamp": time.time(),
        })

        # Suggest contextual follow-ups
        follow_ups = [
            f"Now break this down further",
            f"Show only the top 5 records",
            f"Show the trend over time",
        ]

        return ChatResponse(
            question=question,
            sql=sanitized_sql,
            execution=exec_result,
            chart=chart_spec,
            explanation=explanation,
            follow_up_questions=follow_ups,
            thinking_steps=thinking_steps,
            is_clarification=False,
        )
