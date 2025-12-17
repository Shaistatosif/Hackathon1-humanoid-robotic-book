"""Progress and bookmark models for user learning tracking.

Tracks reading progress, bookmarks, and learning history.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class ProgressStatus(str, PyEnum):
    """Reading progress status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ReadingProgress(Base):
    """Track user reading progress per chapter.

    Attributes:
        id: Unique identifier.
        user_id: Reference to user.
        chapter_id: Reference to chapter.
        status: Current reading status.
        progress_percent: Percentage of chapter read (0-100).
        time_spent_seconds: Total time spent reading.
        last_position: Last reading position (scroll percentage).
        started_at: When user first opened chapter.
        completed_at: When user completed chapter.
        updated_at: Last activity timestamp.
    """

    __tablename__ = "reading_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "chapter_id", name="uq_user_chapter_progress"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chapter_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=ProgressStatus.NOT_STARTED,
        nullable=False,
    )
    progress_percent: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    time_spent_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    last_position: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="reading_progress")
    chapter = relationship("Chapter", backref="reading_progress")

    def __repr__(self) -> str:
        """String representation."""
        return f"<ReadingProgress {self.user_id}:{self.chapter_id} {self.progress_percent}%>"


class Bookmark(Base):
    """User bookmarks for chapters and sections.

    Attributes:
        id: Unique identifier.
        user_id: Reference to user.
        chapter_id: Reference to chapter.
        section_id: Optional section anchor within chapter.
        title: Bookmark display title.
        note: Optional user note.
        position: Scroll position when bookmarked.
        created_at: Bookmark creation time.
    """

    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "chapter_id", "section_id", name="uq_user_bookmark"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chapter_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    position: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="bookmarks")
    chapter = relationship("Chapter", backref="bookmarks")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Bookmark {self.user_id}:{self.chapter_id} '{self.title}'>"
