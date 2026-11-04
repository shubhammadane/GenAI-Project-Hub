import io
import uuid
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.config import settings
from app.core.engine import session_manager
from app.core.security import validate_uploaded_file
from app.models.schemas import UploadResponse
from app.services.llm_provider import get_llm_client
from app.services.profiler import profile_dataframe

router = APIRouter(prefix="/api", tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts CSV or Excel (.xlsx) file, validates format and size,
    loads into an isolated DuckDB session, profiles columns, and returns
    preview + schema + suggested starter questions.
    """
    ext, table_name = validate_uploaded_file(file)

    # Read bytes with size cap
    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.max_upload_size_mb} MB.",
        )

    # Parse into pandas DataFrame
    try:
        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(content))
        else:  # .xlsx, .xls
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse file: {str(e)}",
        )

    if df.empty or len(df.columns) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file contains no data or columns.",
        )

    # Clean column headers
    df.columns = [str(c).strip().replace(" ", "_").replace("-", "_") for c in df.columns]

    # Initialize isolated DuckDB session
    session_id = str(uuid.uuid4())
    session = session_manager.get_or_create(session_id)
    session.filename = file.filename or "uploaded_data"
    session.register_dataframe(table_name, df)

    # Profile dataset
    profile = profile_dataframe(df, table_name)
    session.profile = profile

    # Generate 5 suggested starter questions
    llm = get_llm_client()
    suggested_questions = llm.generate_suggested_questions(profile)

    return UploadResponse(
        session_id=session_id,
        filename=session.filename,
        table_name=table_name,
        profile=profile,
        suggested_questions=suggested_questions,
    )
