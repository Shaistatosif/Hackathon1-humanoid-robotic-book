"""RAG API router.

Provides endpoints for RAG-based question answering and chat session management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user_optional
from src.models.user import User
from src.services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["RAG Chatbot"])


# Request/Response schemas
class QueryRequest(BaseModel):
    """RAG query request."""

    question: str = Field(..., min_length=3, max_length=1000)
    session_id: str | None = Field(None, description="Existing session ID")
    language: str = Field("en", pattern="^(en|ur)$")


class CitationResponse(BaseModel):
    """Citation in RAG response."""

    chapter_id: str
    chapter_title: str
    section_id: str
    section_title: str
    text: str
    relevance_score: float


class QueryResponse(BaseModel):
    """RAG query response."""

    answer: str
    citations: list[CitationResponse]
    is_out_of_scope: bool
    confidence: float
    session_id: str | None = None


class SessionResponse(BaseModel):
    """Chat session response."""

    session_id: str
    created_at: str


class MessageResponse(BaseModel):
    """Chat message in history."""

    id: str
    role: str
    content: str
    citations: list[dict] | None
    created_at: str


class HistoryResponse(BaseModel):
    """Chat history response."""

    session_id: str
    messages: list[MessageResponse]


class CreateSessionRequest(BaseModel):
    """Create session request."""

    pass  # No fields needed, user is optional


@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
) -> QueryResponse:
    """Submit a question to the RAG chatbot.

    The chatbot will:
    1. Search the textbook content for relevant information
    2. Generate an answer based on the retrieved context
    3. Provide citations to the source content

    Args:
        request: Query request with question and optional session ID.
        db: Database session.
        user: Optional authenticated user.

    Returns:
        Answer with citations and metadata.
    """
    rag_service = RAGService(db)

    # Create session if not provided
    session_id = request.session_id
    if not session_id:
        session = await rag_service.create_session(
            user_id=user.id if user else None
        )
        session_id = session.id

    # Process query
    response = await rag_service.query(
        question=request.question,
        session_id=session_id,
        user_id=user.id if user else None,
        language=request.language,
    )

    return QueryResponse(
        answer=response.answer,
        citations=[
            CitationResponse(
                chapter_id=c.chapter_id,
                chapter_title=c.chapter_title,
                section_id=c.section_id,
                section_title=c.section_title,
                text=c.text,
                relevance_score=c.relevance_score,
            )
            for c in response.citations
        ],
        is_out_of_scope=response.is_out_of_scope,
        confidence=response.confidence,
        session_id=session_id,
    )


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
) -> SessionResponse:
    """Create a new chat session.

    Sessions track conversation history and can be associated with authenticated users.

    Args:
        db: Database session.
        user: Optional authenticated user.

    Returns:
        Created session info.
    """
    rag_service = RAGService(db)
    session = await rag_service.create_session(
        user_id=user.id if user else None
    )

    return SessionResponse(
        session_id=session.id,
        created_at=session.created_at.isoformat(),
    )


@router.get("/sessions/{session_id}/history", response_model=HistoryResponse)
async def get_session_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
) -> HistoryResponse:
    """Get chat history for a session.

    Args:
        session_id: Chat session ID.
        db: Database session.
        user: Optional authenticated user.

    Returns:
        List of messages in the session.

    Raises:
        HTTPException: If session not found.
    """
    rag_service = RAGService(db)
    messages = await rag_service.get_session_history(session_id)

    if not messages:
        # Check if session exists (could be empty)
        from sqlalchemy import select
        from src.models.chat import ChatSession
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

    return HistoryResponse(
        session_id=session_id,
        messages=[
            MessageResponse(
                id=msg["id"],
                role=msg["role"],
                content=msg["content"],
                citations=msg["citations"],
                created_at=msg["created_at"],
            )
            for msg in messages
        ],
    )


@router.get("/health")
async def rag_health():
    """Check RAG service health.

    Verifies Qdrant connection and collection existence.
    """
    from src.core.qdrant import qdrant_client
    from src.core.config import settings

    try:
        collections = qdrant_client.get_collections()
        collection_exists = any(
            c.name == settings.qdrant_collection
            for c in collections.collections
        )

        return {
            "status": "healthy",
            "qdrant_connected": True,
            "collection_exists": collection_exists,
            "collection_name": settings.qdrant_collection,
        }
    except Exception as e:
        return {
            "status": "degraded",
            "qdrant_connected": False,
            "error": str(e),
        }
