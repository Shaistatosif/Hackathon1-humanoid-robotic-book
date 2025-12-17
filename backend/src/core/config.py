"""Application configuration module.

Loads environment variables and provides typed configuration settings.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./app.db"

    # Gemini API
    gemini_api_key: str = ""
    embedding_model: str = "text-embedding-004"
    generation_model: str = "gemini-1.5-flash"
    generation_temperature: float = 0.0

    # Qdrant
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "textbook_chunks"

    # Authentication
    better_auth_secret: str = ""
    better_auth_url: str = "http://localhost:8000"
    session_expire_minutes: int = 1440  # 24 hours

    # CORS
    frontend_url: str = "http://localhost:3000"

    # RAG
    rag_top_k: int = 5

    @property
    def cors_origins(self) -> list[str]:
        """Get list of allowed CORS origins."""
        origins = [self.frontend_url]
        if self.environment == "development":
            origins.extend([
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ])
        return list(set(origins))

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
