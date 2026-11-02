import uuid
from typing import List, Optional
import pandas as pd
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, inspect, text
from app.core.db_connectors import ReadOnlyDatabaseConnector
from app.core.engine import session_manager
from app.core.security import sanitize_table_name
from app.models.schemas import UploadResponse
from app.services.llm_provider import get_llm_client
from app.services.profiler import profile_dataframe

router = APIRouter(prefix="/api/connect-db", tags=["Database Connector"])


class ConnectDbRequest(BaseModel):
    connection_url: str
    table_name: Optional[str] = None


class ListTablesResponse(BaseModel):
    tables: List[str]


@router.post("/list-tables", response_model=ListTablesResponse)
async def list_database_tables(request: ConnectDbRequest):
    """Lists available tables from a remote database connection."""
    try:
        tables = ReadOnlyDatabaseConnector.list_tables(request.connection_url)
        return ListTablesResponse(tables=tables)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not connect to database: {str(e)}",
        )


@router.post("", response_model=UploadResponse)
async def connect_and_import_table(request: ConnectDbRequest):
    """
    Connects to an external SQL database (read-only), reads table into
    an isolated DuckDB session, and returns profile + suggested questions.
    """
    try:
        tables = ReadOnlyDatabaseConnector.list_tables(request.connection_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection failed: {str(e)}",
        )

    if not tables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The database contains no accessible tables.",
        )

    selected_table = request.table_name or tables[0]
    if selected_table not in tables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table '{selected_table}' not found in database. Available: {tables}",
        )

    # Read up to 50,000 rows safely
    engine = ReadOnlyDatabaseConnector.create_safe_engine(request.connection_url)
    try:
        with engine.connect() as conn:
            query = f'SELECT * FROM "{selected_table}" LIMIT 50000'
            df = pd.read_sql_query(text(query), conn)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read table '{selected_table}': {str(e)}",
        )
    finally:
        engine.dispose()

    # Clean headers
    df.columns = [str(c).strip().replace(" ", "_").replace("-", "_") for c in df.columns]
    sanitized_name = sanitize_table_name(selected_table)

    # Load into isolated DuckDB session
    session_id = str(uuid.uuid4())
    session = session_manager.get_or_create(session_id)
    session.filename = f"db:{selected_table}"
    session.register_dataframe(sanitized_name, df)

    # Profile table
    profile = profile_dataframe(df, sanitized_name)
    session.profile = profile

    # Suggested questions
    llm = get_llm_client()
    suggested = llm.generate_suggested_questions(profile)

    return UploadResponse(
        session_id=session_id,
        filename=session.filename,
        table_name=sanitized_name,
        profile=profile,
        suggested_questions=suggested,
    )
