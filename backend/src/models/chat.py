"""Chat models for RAG conversation history.

Stores chat sessions and messages with citations.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class MessageRole(str, PyEnum):
    """Role of message sender."""

    USER = "user"
    ASSISTANT = "assistant"


class ChatSession(Base):
    """Chat session for RAG conversations.

    Attributes:
        id: Unique session identifier.
        user_id: Optional user ID (null for anonymous).
        created_at: Session creation timestamp.
        updated_at: Last message timestamp.
    """

    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
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

    # Relationships
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self) -> str:
        """String representation of ChatSession."""
        return f"<ChatSession {self.id}>"


class ChatMessage(Base):
    """Individual message in a chat session.

    Attributes:
        id: Unique message identifier.
        session_id: Parent session ID.
        role: Message sender role (user/assistant).
        content: Message text content.
        citations_json: JSON string of citations for assistant messages.
        created_at: Message timestamp.
    """

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        Enum(MessageRole),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    citations_json: Mapped[str | None] = mapped_column(
        Text,  # JSON string of citations
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    session: Mapped["ChatSession"] = relationship(
        "ChatSession",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        """String representation of ChatMessage."""
        return f"<ChatMessage {self.id} ({self.role})>"

    @property
    def citations(self) -> list[dict] | None:
        """Parse citations from JSON string."""
        if not self.citations_json:
            return None
        import json
        try:
            return json.loads(self.citations_json)
        except json.JSONDecodeError:
            return None

    @citations.setter
    def citations(self, value: list[dict] | None) -> None:
        """Set citations as JSON string."""
        if value is None:
            self.citations_json = None
        else:
            import json
            self.citations_json = json.dumps(value)
