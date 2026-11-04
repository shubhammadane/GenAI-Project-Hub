import re
import os
from typing import Tuple
from fastapi import HTTPException, UploadFile, status
from app.config import settings

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def sanitize_table_name(filename: str) -> str:
    """Derives a clean, SQL-safe table identifier from a raw filename."""
    base_name = os.path.splitext(os.path.basename(filename))[0]
    # Replace non-alphanumeric chars with underscore
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", base_name).strip("_").lower()
    if not sanitized or sanitized[0].isdigit():
        sanitized = f"t_{sanitized}"
    return sanitized[:64]


def validate_uploaded_file(file: UploadFile) -> Tuple[str, str]:
    """Validates the uploaded file extension and content headers."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Only CSV and Excel (.xlsx, .xls) files are supported.",
        )

    table_name = sanitize_table_name(file.filename)
    return ext, table_name


def escape_data_for_prompt(text: str) -> str:
    """Escapes user and cell data strings to prevent prompt injection or markdown breakage."""
    if not isinstance(text, str):
        text = str(text)
    # Replace prompt-breaking tokens
    sanitized = text.replace("<", "&lt;").replace(">", "&gt;").replace("\x00", "")
    return sanitized.strip()
