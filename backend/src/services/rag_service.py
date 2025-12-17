"""RAG (Retrieval-Augmented Generation) Service.

Provides question answering with citations from textbook content.
"""

import json
from dataclasses import dataclass

from qdrant_client import QdrantClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.gemini import gemini_client
from src.core.qdrant import qdrant_client
from src.models.chat import ChatMessage, ChatSession, MessageRole


@dataclass
class Citation:
    """A citation to textbook content."""

    chapter_id: str
    chapter_title: str
    section_id: str
    section_title: str
    text: str
    relevance_score: float

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "chapter_id": self.chapter_id,
            "chapter_title": self.chapter_title,
            "section_id": self.section_id,
            "section_title": self.section_title,
            "text": self.text,
            "relevance_score": self.relevance_score,
        }


@dataclass
class RAGResponse:
    """Response from RAG query."""

    answer: str
    citations: list[Citation]
    is_out_of_scope: bool
    confidence: float


# System prompt for RAG generation
RAG_SYSTEM_PROMPT = """You are an educational assistant for a humanoid robotics textbook. Your role is to answer questions based ONLY on the provided context from the textbook.

IMPORTANT RULES:
1. ONLY use information from the provided context to answer questions
2. If the question cannot be answered from the context, say "I don't have information about that in the textbook"
3. Always cite the specific chapter and section when providing information
4. Be concise but thorough in your explanations
5. Use technical terms appropriately for an academic audience
6. If asked about topics outside humanoid robotics, politely redirect to the textbook content

FORMAT YOUR RESPONSE:
- Provide a clear, educational answer
- Reference specific chapters/sections naturally in your response
- Do not make up information not in the context"""

OUT_OF_SCOPE_KEYWORDS = [
    "weather", "news", "sports", "politics", "entertainment",
    "personal advice", "medical advice", "legal advice",
    "stock", "crypto", "investment", "recipe", "cooking",
]


class RAGService:
    """Service for RAG-based question answering."""

    def __init__(
        self,
        db: AsyncSession,
        qdrant: QdrantClient | None = None,
    ):
        """Initialize RAG service.

        Args:
            db: Database session for chat history.
            qdrant: Optional Qdrant client (uses singleton if not provided).
        """
        self.db = db
        self.qdrant = qdrant or qdrant_client
        self.collection_name = settings.qdrant_collection
        self.top_k = settings.rag_top_k

    def _is_out_of_scope(self, query: str) -> bool:
        """Check if query is likely out of scope.

        Args:
            query: User's question.

        Returns:
            True if query appears to be out of scope.
        """
        query_lower = query.lower()

        # Check for out-of-scope keywords
        for keyword in OUT_OF_SCOPE_KEYWORDS:
            if keyword in query_lower:
                return True

        # Check for personal questions
        personal_patterns = ["my ", "i am", "i'm", "help me with my"]
        for pattern in personal_patterns:
            if pattern in query_lower and "robot" not in query_lower:
                return True

        return False

    async def _retrieve_context(
        self,
        query: str,
        language: str = "en"
    ) -> list[Citation]:
        """Retrieve relevant context from vector store.

        Args:
            query: User's question.
            language: Language filter (en/ur).

        Returns:
            List of relevant citations.
        """
        # Generate query embedding
        query_embedding = await gemini_client.generate_query_embedding(query)

        # Search Qdrant
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            query_filter = None
            if language:
                query_filter = Filter(
                    must=[FieldCondition(key="language", match=MatchValue(value=language))]
                )

            results = self.qdrant.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                query_filter=query_filter,
                limit=self.top_k,
                score_threshold=0.5,  # Minimum relevance threshold
            ).points
        except Exception as e:
            print(f"Qdrant search error: {e}")
            return []

        # Convert to citations
        citations = []
        for result in results:
            payload = result.payload or {}
            citation = Citation(
                chapter_id=str(payload.get("chapter_id", "")),
                chapter_title=str(payload.get("chapter_title", "")),
                section_id=str(payload.get("section_id", "")),
                section_title=str(payload.get("section_title", "")),
                text=str(payload.get("chunk_text", "")),
                relevance_score=result.score,
            )
            citations.append(citation)

        return citations

    def _build_context_prompt(self, citations: list[Citation]) -> str:
        """Build context string from citations.

        Args:
            citations: List of relevant citations.

        Returns:
            Formatted context string.
        """
        if not citations:
            return "No relevant context found in the textbook."

        context_parts = []
        for i, citation in enumerate(citations, 1):
            context_parts.append(
                f"[{i}] From {citation.chapter_title} - {citation.section_title}:\n"
                f"{citation.text}\n"
            )

        return "\n".join(context_parts)

    async def _generate_answer(
        self,
        query: str,
        context: str,
        citations: list[Citation],
    ) -> RAGResponse:
        """Generate answer using Gemini.

        Args:
            query: User's question.
            context: Retrieved context string.
            citations: Source citations.

        Returns:
            RAG response with answer and citations.
        """
        # Build prompt
        prompt = f"""Context from the textbook:
{context}

User Question: {query}

Please answer the question based on the context provided. If the context doesn't contain relevant information, say so."""

        # Generate response
        try:
            answer = await gemini_client.generate_text(
                prompt=prompt,
                system_instruction=RAG_SYSTEM_PROMPT,
            )
        except Exception as e:
            print(f"Generation error: {e}")
            answer = "I'm sorry, I encountered an error generating a response. Please try again."

        # Calculate confidence based on citation relevance
        if citations:
            avg_score = sum(c.relevance_score for c in citations) / len(citations)
            confidence = min(avg_score, 1.0)
        else:
            confidence = 0.0

        # Check if answer indicates out of scope
        out_of_scope_phrases = [
            "don't have information",
            "not covered in",
            "outside the scope",
            "cannot answer",
            "no relevant context",
        ]
        is_out_of_scope = any(
            phrase in answer.lower() for phrase in out_of_scope_phrases
        )

        return RAGResponse(
            answer=answer,
            citations=citations,
            is_out_of_scope=is_out_of_scope,
            confidence=confidence,
        )

    async def query(
        self,
        question: str,
        session_id: str | None = None,
        user_id: str | None = None,
        language: str = "en",
    ) -> RAGResponse:
        """Process a RAG query.

        Args:
            question: User's question.
            session_id: Optional existing session ID.
            user_id: Optional user ID for session association.
            language: Content language (en/ur).

        Returns:
            RAG response with answer and citations.
        """
        # Check for obviously out-of-scope queries
        if self._is_out_of_scope(question):
            return RAGResponse(
                answer=(
                    "I'm designed to help with questions about humanoid robotics "
                    "from the textbook. Your question appears to be outside that scope. "
                    "Please ask about topics covered in the textbook, such as robot "
                    "components, sensors, actuators, or control systems."
                ),
                citations=[],
                is_out_of_scope=True,
                confidence=1.0,
            )

        # Retrieve relevant context
        citations = await self._retrieve_context(question, language)

        # Build context prompt
        context = self._build_context_prompt(citations)

        # Generate answer
        response = await self._generate_answer(question, context, citations)

        # Store in chat history if session provided
        if session_id:
            await self._save_to_history(
                session_id=session_id,
                user_id=user_id,
                question=question,
                response=response,
            )

        return response

    async def _save_to_history(
        self,
        session_id: str,
        user_id: str | None,
        question: str,
        response: RAGResponse,
    ) -> None:
        """Save query and response to chat history.

        Args:
            session_id: Chat session ID.
            user_id: Optional user ID.
            question: User's question.
            response: RAG response.
        """
        # Get or create session
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            session = ChatSession(id=session_id, user_id=user_id)
            self.db.add(session)

        # Add user message
        user_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.USER,
            content=question,
        )
        self.db.add(user_message)

        # Add assistant message with citations
        citations_data = [c.to_dict() for c in response.citations]
        assistant_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=response.answer,
            citations_json=json.dumps(citations_data) if citations_data else None,
        )
        self.db.add(assistant_message)

        await self.db.flush()

    async def get_session_history(
        self,
        session_id: str,
    ) -> list[dict]:
        """Get chat history for a session.

        Args:
            session_id: Chat session ID.

        Returns:
            List of message dictionaries.
        """
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        messages = result.scalars().all()

        return [
            {
                "id": msg.id,
                "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                "content": msg.content,
                "citations": msg.citations,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]

    async def create_session(self, user_id: str | None = None) -> ChatSession:
        """Create a new chat session.

        Args:
            user_id: Optional user ID to associate with session.

        Returns:
            Created ChatSession.
        """
        session = ChatSession(user_id=user_id)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session
