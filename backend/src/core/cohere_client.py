"""Cohere API client wrapper.

Provides text embedding capabilities using Cohere's embed API.
"""

from functools import lru_cache

import cohere

from src.core.config import settings


class CohereClient:
    """Wrapper for Cohere API operations."""

    def __init__(self) -> None:
        """Initialize the Cohere client."""
        self._client: cohere.AsyncClient | None = None
        self._sync_client: cohere.Client | None = None
        self._embedding_model = settings.cohere_embedding_model

    @property
    def client(self) -> cohere.AsyncClient:
        """Get or create the async Cohere client instance."""
        if self._client is None:
            if not settings.cohere_api_key:
                raise ValueError("COHERE_API_KEY not configured")
            self._client = cohere.AsyncClient(api_key=settings.cohere_api_key)
        return self._client

    @property
    def sync_client(self) -> cohere.Client:
        """Get or create the sync Cohere client instance."""
        if self._sync_client is None:
            if not settings.cohere_api_key:
                raise ValueError("COHERE_API_KEY not configured")
            self._sync_client = cohere.Client(api_key=settings.cohere_api_key)
        return self._sync_client

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        response = await self.client.embed(
            texts=[text],
            model=self._embedding_model,
            input_type="search_document",
            embedding_types=["float"],
        )
        return response.embeddings.float_[0]

    async def generate_embeddings_batch(
        self,
        texts: list[str],
        input_type: str = "search_document"
    ) -> list[list[float]]:
        """Generate embedding vectors for multiple texts.

        Args:
            texts: List of texts to embed.
            input_type: Type of input (search_document, search_query, classification, clustering).

        Returns:
            List of embedding vectors.
        """
        response = await self.client.embed(
            texts=texts,
            model=self._embedding_model,
            input_type=input_type,
            embedding_types=["float"],
        )
        return response.embeddings.float_

    async def generate_query_embedding(self, query: str) -> list[float]:
        """Generate an embedding vector optimized for queries.

        Args:
            query: Query text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        response = await self.client.embed(
            texts=[query],
            model=self._embedding_model,
            input_type="search_query",
            embedding_types=["float"],
        )
        return response.embeddings.float_[0]

    def generate_embedding_sync(self, text: str) -> list[float]:
        """Generate an embedding vector synchronously.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        response = self.sync_client.embed(
            texts=[text],
            model=self._embedding_model,
            input_type="search_document",
            embedding_types=["float"],
        )
        return response.embeddings.float_[0]

    def generate_embeddings_batch_sync(
        self,
        texts: list[str],
        input_type: str = "search_document"
    ) -> list[list[float]]:
        """Generate embedding vectors for multiple texts synchronously.

        Args:
            texts: List of texts to embed.
            input_type: Type of input.

        Returns:
            List of embedding vectors.
        """
        response = self.sync_client.embed(
            texts=texts,
            model=self._embedding_model,
            input_type=input_type,
            embedding_types=["float"],
        )
        return response.embeddings.float_


@lru_cache
def get_cohere_client() -> CohereClient:
    """Get cached Cohere client instance."""
    return CohereClient()


# Singleton client instance
cohere_client = get_cohere_client()
