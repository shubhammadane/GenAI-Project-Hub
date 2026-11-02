import asyncio
import json
import queue
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from app.core.engine import session_manager
from app.models.schemas import ChatRequest, ChatResponse, ThinkingStep
from app.services.sql_agent import SqlAgent

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Executes the conversational text-to-SQL pipeline synchronously:
    context building -> LLM SQL generation -> AST validation ->
    DuckDB execution -> Plotly charting -> grounded explanation.
    """
    if not request.session_id or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both 'session_id' and 'question' are required.",
        )

    if not session_manager.session_exists(request.session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{request.session_id}' not found. Please upload a file first.",
        )

    response = SqlAgent.process_question(
        session_id=request.session_id,
        question=request.question.strip(),
    )
    return response


@router.get("/chat/stream")
async def chat_stream(
    session_id: str = Query(..., description="Session identifier"),
    question: str = Query(..., description="Plain-English question"),
):
    """
    Server-Sent Events (SSE) streaming endpoint that yields real-time
    thinking steps as each pipeline stage executes, followed by the final payload.
    """
    if not session_manager.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    msg_queue: queue.Queue = queue.Queue()

    def progress_callback(step: ThinkingStep):
        msg_queue.put({"type": "step", "payload": step.model_dump()})

    async def event_generator() -> AsyncGenerator[str, None]:
        # Run process_question in a separate thread to keep SSE event loop non-blocking
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            None,
            lambda: SqlAgent.process_question(
                session_id=session_id,
                question=question,
                progress_callback=progress_callback,
            ),
        )

        while not future.done() or not msg_queue.empty():
            try:
                msg = msg_queue.get_nowait()
                yield f"data: {json.dumps(msg)}\n\n"
            except queue.Empty:
                await asyncio.sleep(0.05)

        # Send final complete payload
        final_result: ChatResponse = await future
        yield f"data: {json.dumps({'type': 'result', 'payload': final_result.model_dump()})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
