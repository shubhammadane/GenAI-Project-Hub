import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes_upload import router as upload_router
from app.api.routes_chat import router as chat_router
from app.api.routes_query import router as query_router
from app.api.routes_session import router as session_router
from app.api.routes_export import router as export_router
from app.api.routes_db import router as db_router

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("askdata.audit")

app = FastAPI(
    title="AskData API",
    description="Production-grade AI Data Analyst query engine and conversational analytics pipeline.",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    """Logs every API query, latency, client IP, and HTTP status code for audit compliance."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    logger.info(
        f"AUDIT | client={request.client.host if request.client else 'unknown'} | "
        f"method={request.method} | path={request.url.path} | "
        f"status={response.status_code} | latency={duration_ms}ms"
    )
    return response


# Include Routers
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(query_router)
app.include_router(session_router)
app.include_router(export_router)
app.include_router(db_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Service health and uptime endpoint."""
    return {
        "status": "healthy",
        "service": "AskData AI Analyst",
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
    }
