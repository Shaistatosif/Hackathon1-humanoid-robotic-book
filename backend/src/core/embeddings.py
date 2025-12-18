"""Unified Embedding Service.

Provides a unified interface for generating embeddings using either
Cohere or Google Gemini based on configuration.
"""

from functools import lru_cache
from typing import Protocol

from src.core.config import settings


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        ...

    async def generate_query_embedding(self, query: str) -> list[float]:
        """Generate embedding optimized for queries."""
        ...


class EmbeddingService:
    """Unified embedding service that delegates to configured provider."""

    def __init__(self):
        """Initialize embedding service with configured provider."""
        self._provider = settings.embedding_provider
        self._cohere_client = None
        self._gemini_client = None

    @property
    def dimension(self) -> int:
        """Get embedding dimension for current provider."""
        return settings.embedding_dimension

    def _get_cohere_client(self):
        """Lazy load Cohere client."""
        if self._cohere_client is None:
            from src.core.cohere_client import cohere_client
            self._cohere_client = cohere_client
        return self._cohere_client

    def _get_gemini_client(self):
        """Lazy load Gemini client."""
        if self._gemini_client is None:
            from src.core.gemini import gemini_client
            self._gemini_client = gemini_client
        return self._gemini_client

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text.

        Uses the configured embedding provider (Cohere or Gemini).

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        if self._provider == "cohere":
            return await self._get_cohere_client().generate_embedding(text)
        else:
            return await self._get_gemini_client().generate_embedding(text)

    async def generate_query_embedding(self, query: str) -> list[float]:
        """Generate an embedding vector optimized for queries.

        Uses the configured embedding provider (Cohere or Gemini).

        Args:
            query: Query text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        if self._provider == "cohere":
            return await self._get_cohere_client().generate_query_embedding(query)
        else:
            return await self._get_gemini_client().generate_query_embedding(query)

    async def generate_embeddings_batch(
        self,
        texts: list[str],
        input_type: str = "document"
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.
            input_type: Type of input (document or query).

        Returns:
            List of embedding vectors.
        """
        if self._provider == "cohere":
            cohere_input_type = "search_document" if input_type == "document" else "search_query"
            return await self._get_cohere_client().generate_embeddings_batch(
                texts, cohere_input_type
            )
        else:
            # Gemini doesn't have native batch, process sequentially
            embeddings = []
            for text in texts:
                if input_type == "query":
                    emb = await self._get_gemini_client().generate_query_embedding(text)
                else:
                    emb = await self._get_gemini_client().generate_embedding(text)
                embeddings.append(emb)
            return embeddings


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    return EmbeddingService()


# Singleton service instance
embedding_service = get_embedding_service()
