"""User model for authentication and user data.

Represents registered learners on the platform.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class LanguagePreference(str, PyEnum):
    """Supported language preferences."""

    EN = "en"
    UR = "ur"


class User(Base):
    """User database model.

    Attributes:
        id: Unique identifier (UUID).
        email: Login email address (unique).
        password_hash: Bcrypt hashed password.
        display_name: Optional display name.
        language_pref: Preferred language (en/ur).
        created_at: Account creation timestamp.
        updated_at: Last update timestamp.
        is_verified: Email verification status.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    display_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    language_pref: Mapped[str] = mapped_column(
        Enum(LanguagePreference),
        default=LanguagePreference.EN,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User {self.email}>"
