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

    # Cohere API
    cohere_api_key: str = ""
    cohere_embedding_model: str = "embed-english-v3.0"

    # Embedding provider selection: "gemini" or "cohere"
    embedding_provider: Literal["gemini", "cohere"] = "cohere"

    # Qdrant
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "textbook_chunks"
    qdrant_path: str = "./qdrant_data"  # Local storage path

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
        # Production Vercel URLs
        origins.extend([
            "https://hackathon-one-humanoid-robotic-book.vercel.app",
            "https://hackathon1-humanoid-robotic-book.vercel.app",
            "https://frontend-psi-eosin-17.vercel.app",
            "https://frontend-shaista-tosifs-projects.vercel.app",
        ])
        # Also allow any vercel.app subdomain for preview deployments
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

    @property
    def async_database_url(self) -> str:
        """Get async-compatible database URL.

        Converts standard PostgreSQL URLs to async format for SQLAlchemy.
        Supports Neon PostgreSQL serverless connections.
        """
        url = self.database_url

        # Handle PostgreSQL URLs (including Neon)
        if url.startswith("postgresql://") or url.startswith("postgres://"):
            # Remove sslmode and channel_binding from URL - asyncpg doesn't support them
            # SSL is handled via connect_args in database.py
            if "?" in url:
                base_url, params = url.split("?", 1)
                # Filter out unsupported asyncpg parameters
                param_list = params.split("&")
                filtered_params = [
                    p for p in param_list
                    if not p.startswith("sslmode=") and not p.startswith("channel_binding=")
                ]
                if filtered_params:
                    url = f"{base_url}?{'&'.join(filtered_params)}"
                else:
                    url = base_url

            # Convert to asyncpg format
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://")
            else:
                return url.replace("postgres://", "postgresql+asyncpg://")

        # SQLite already has async format or needs aiosqlite
        if url.startswith("sqlite:///") and "+aiosqlite" not in url:
            return url.replace("sqlite:///", "sqlite+aiosqlite:///")

        return url

    @property
    def is_postgres(self) -> bool:
        """Check if using PostgreSQL database."""
        return "postgresql" in self.database_url or "postgres" in self.database_url

    @property
    def embedding_dimension(self) -> int:
        """Get embedding dimension based on provider."""
        if self.embedding_provider == "cohere":
            # Cohere embed-english-v3.0 produces 1024-dim vectors
            return 1024
        else:
            # Gemini text-embedding-004 produces 768-dim vectors
            return 768


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
