from fastapi import APIRouter, HTTPException, status
from app.config import settings
from app.core.engine import session_manager
from app.core.validator import SqlValidator
from app.models.schemas import ChartSpec, RunSqlRequest, RunSqlResponse
from app.services.llm_provider import get_llm_client

router = APIRouter(prefix="/api", tags=["Query"])


@router.post("/run-sql", response_model=RunSqlResponse)
async def run_sql(request: RunSqlRequest):
    """
    Executes a user-edited SQL query through the same strict AST validator,
    runs it in the isolated DuckDB session, and generates an updated chart.
    """
    session = session_manager.get(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{request.session_id}' not found.",
        )

    # Validate against allowed tables
    validation = SqlValidator.validate_and_sanitize(
        sql=request.sql,
        allowed_tables=session.list_tables(),
        default_limit=settings.default_row_limit,
        max_limit=settings.max_row_limit,
    )

    if not validation.is_valid:
        return RunSqlResponse(
            sql=request.sql,
            execution=session.execute_query("SELECT 1 WHERE 1=0"),  # empty result
            is_valid=False,
            error=validation.error_message,
        )

    sanitized = validation.sanitized_sql or request.sql
    exec_result = session.execute_query(sanitized)

    # Optional chart generation for the query
    chart_spec = None
    if not exec_result.error and exec_result.rows:
        llm = get_llm_client()
        chart_dict = llm.generate_chart_spec(
            question="User edited query",
            sql=sanitized,
            columns=exec_result.columns,
            sample_rows=exec_result.rows[:20],
        )
        chart_spec = ChartSpec(**chart_dict)

    return RunSqlResponse(
        sql=sanitized,
        execution=exec_result,
        chart=chart_spec,
        is_valid=True,
        error=exec_result.error,
    )
