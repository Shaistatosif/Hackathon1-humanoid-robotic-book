#!/usr/bin/env python3
"""
Database Initialization Script.

This script initializes the database schema for both SQLite and PostgreSQL.
Supports Neon PostgreSQL serverless connections.

Usage:
    python -m scripts.init_db [--check]
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import text

from src.core.config import settings
from src.core.database import Base, engine, init_db


async def check_connection() -> bool:
    """Check database connection.

    Returns:
        True if connection successful, False otherwise.
    """
    try:
        async with engine.connect() as conn:
            if settings.is_postgres:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"Connected to PostgreSQL: {version}")
            else:
                result = await conn.execute(text("SELECT sqlite_version()"))
                version = result.scalar()
                print(f"Connected to SQLite: {version}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


async def list_tables() -> list[str]:
    """List all tables in the database.

    Returns:
        List of table names.
    """
    async with engine.connect() as conn:
        if settings.is_postgres:
            result = await conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            ))
        else:
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ))
        tables = [row[0] for row in result.fetchall()]
    return tables


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Initialize database")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check connection, don't create tables"
    )
    args = parser.parse_args()

    print("Database Configuration:")
    print(f"  URL: {settings.database_url[:50]}...")
    print(f"  Async URL: {settings.async_database_url[:50]}...")
    print(f"  PostgreSQL: {settings.is_postgres}")
    print(f"  Environment: {settings.environment}")
    print()

    # Check connection
    print("Checking database connection...")
    if not await check_connection():
        print("Failed to connect to database")
        sys.exit(1)

    if args.check:
        # List existing tables
        tables = await list_tables()
        print(f"\nExisting tables ({len(tables)}):")
        for table in sorted(tables):
            print(f"  - {table}")
        return

    # Import models to register them with SQLAlchemy
    print("\nImporting models...")
    from src.models import user, chapter, chat, quiz, progress  # noqa: F401

    # Create all tables
    print("Creating database tables...")
    await init_db()

    # List created tables
    tables = await list_tables()
    print(f"\nCreated tables ({len(tables)}):")
    for table in sorted(tables):
        print(f"  - {table}")

    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    asyncio.run(main())
