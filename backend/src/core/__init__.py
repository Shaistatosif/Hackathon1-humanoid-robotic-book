# Core configuration package
from src.core.config import Settings, get_settings, settings
from src.core.database import Base, async_session_maker, engine, get_db, init_db
from src.core.gemini import GeminiClient, gemini_client, get_gemini_client
from src.core.qdrant import get_qdrant_client, qdrant_client
from src.core.security import (
    get_current_user,
    get_current_user_optional,
    require_verified_user,
)

__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "Base",
    "engine",
    "async_session_maker",
    "get_db",
    "init_db",
    "GeminiClient",
    "gemini_client",
    "get_gemini_client",
    "qdrant_client",
    "get_qdrant_client",
    "get_current_user",
    "get_current_user_optional",
    "require_verified_user",
]
