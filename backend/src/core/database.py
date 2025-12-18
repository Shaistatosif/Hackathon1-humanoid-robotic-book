"""SQLAlchemy database setup with async support for SQLite and PostgreSQL.

Provides database engine, session management, and base model class.
Supports Neon PostgreSQL serverless connections.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from src.core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


def create_engine():
    """Create async database engine with appropriate configuration.

    For PostgreSQL (including Neon), uses NullPool for serverless compatibility.
    For SQLite, uses default connection pooling.
    """
    database_url = settings.async_database_url

    # Engine configuration
    engine_kwargs = {
        "echo": settings.debug,
        "future": True,
    }

    # For PostgreSQL/Neon serverless, disable connection pooling
    # This prevents "connection closed" errors in serverless environments
    if settings.is_postgres:
        engine_kwargs["poolclass"] = NullPool
        # SSL configuration for Neon and other cloud PostgreSQL
        # asyncpg requires boolean or SSLContext, not string values
        if settings.is_production:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            engine_kwargs["connect_args"] = {"ssl": ssl_context}
        else:
            engine_kwargs["connect_args"] = {"ssl": False}

    return create_async_engine(database_url, **engine_kwargs)


# Create async engine
engine = create_engine()

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database by creating all tables.

    Called on application startup to ensure tables exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session.

    Yields:
        AsyncSession: Database session for the request.

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
