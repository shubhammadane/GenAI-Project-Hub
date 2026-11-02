import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM Settings
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "gemini"  # "gemini", "openai", "anthropic", "mock"
    llm_model: str = "gemini-1.5-flash"

    # Execution Guardrails
    max_upload_size_mb: int = 50
    query_timeout_seconds: int = 10
    default_row_limit: int = 500
    max_row_limit: int = 10000

    # Networking & Security
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000", "*"]
    rate_limit_per_minute: int = 60
    database_readonly_url: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
