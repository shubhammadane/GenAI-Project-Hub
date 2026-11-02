import io
from datetime import datetime, timezone
import pandas as pd
from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import PlainTextResponse
from app.core.engine import session_manager

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/{session_id}/report", response_class=PlainTextResponse)
async def export_session_markdown(session_id: str):
    """Generates and downloads a comprehensive Markdown session report."""
    session = session_manager.get(session_id)
    if not session or not session.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    profile = session.profile
    lines = [
        f"# AskData Analytical Report",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Source File:** `{session.filename}`",
        f"**Active Table:** `{session.table_name}`",
        f"**Dimensions:** {profile.row_count:,} rows | {profile.column_count} columns",
        "",
        "---",
        "",
        "## 1. Dataset Schema & Column Profile",
        "",
        "| Column Name | SQL Type | Nulls Count | Null % | Unique Values | Value Range |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for col in profile.columns:
        range_str = f"[{col.min_value} to {col.max_value}]" if col.min_value is not None else "N/A"
        lines.append(
            f"| `{col.name}` | `{col.data_type}` | {col.null_count} | {col.null_percentage}% | {col.unique_count} | {range_str} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Analysis & Investigation History")
    lines.append("")

    if not session.history:
        lines.append("*No questions have been queried in this session yet.*")
    else:
        for idx, entry in enumerate(session.history, 1):
            lines.append(f"### Inquiry #{idx}: {entry.get('question')}")
            lines.append("")
            lines.append("```sql")
            lines.append(entry.get("sql", "-- No SQL"))
            lines.append("```")
            lines.append("")
            if entry.get("explanation"):
                lines.append(f"> **Insight:** {entry.get('explanation')}")
                lines.append("")
            lines.append("---")
            lines.append("")

    lines.append("## 3. Security & Compliance Guarantee")
    lines.append("- Queries executed in an isolated DuckDB instance with `enable_external_access = false`.")
    lines.append("- Read-only validation enforced via `sqlglot` AST parsing.")

    report_content = "\n".join(lines)
    filename = f"AskData_Report_{session.table_name}.md"

    return PlainTextResponse(
        content=report_content,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{session_id}/csv")
async def export_latest_csv(session_id: str):
    """Downloads the most recently executed query result (or full table) as CSV."""
    session = session_manager.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    # Use latest SQL query from history, or default to whole table
    if session.history and session.history[-1].get("sql"):
        sql = session.history[-1]["sql"]
    else:
        sql = f'SELECT * FROM "{session.table_name}" LIMIT 1000'

    res = session.execute_query(sql)
    if res.error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch data for export: {res.error}",
        )

    df = pd.DataFrame(res.rows)
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{session.table_name}_export.csv"'
        },
    )
