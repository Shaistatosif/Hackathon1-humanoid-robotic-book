"""Chapter model for textbook content metadata.

Represents major sections of the textbook.
"""

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Chapter(Base):
    """Chapter database model.

    Attributes:
        id: Slug-based ID (e.g., "chapter-1").
        title: Chapter title.
        slug: URL-friendly identifier.
        order: Display order (1, 2, 3...).
        description: Brief chapter description.
        summary: AI-generated summary.
        content_path: Path to English markdown file.
        urdu_path: Path to Urdu markdown file.
    """

    __tablename__ = "chapters"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    content_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    urdu_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    def __repr__(self) -> str:
        """String representation of Chapter."""
        return f"<Chapter {self.id}: {self.title}>"
