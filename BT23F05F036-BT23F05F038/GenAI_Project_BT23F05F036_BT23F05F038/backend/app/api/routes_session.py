from fastapi import APIRouter, HTTPException, status
from app.core.engine import session_manager
from app.models.schemas import SessionState

router = APIRouter(prefix="/api", tags=["Session"])


@router.get("/session/{session_id}", response_model=SessionState)
async def get_session(session_id: str):
    """Retrieves session profile, table schema, and query history."""
    state = session_manager.to_session_state(session_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
    return state
