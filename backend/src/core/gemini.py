"""Gemini API client wrapper.

Provides text embedding and generation capabilities using Google's Gemini API.
"""

from functools import lru_cache

from google import genai
from google.genai import types

from src.core.config import settings


@lru_cache
def get_client() -> genai.Client:
    """Get configured Gemini client."""
    return genai.Client(api_key=settings.gemini_api_key)


class GeminiClient:
    """Wrapper for Gemini API operations."""

    def __init__(self) -> None:
        """Initialize the Gemini client."""
        self._client = get_client()
        self._embedding_model = settings.embedding_model

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        """Generate text using Gemini.

        Args:
            prompt: The user prompt to generate from.
            system_instruction: Optional system instruction for context.

        Returns:
            Generated text response.
        """
        config = types.GenerateContentConfig(
            temperature=settings.generation_temperature,
        )
        if system_instruction:
            config.system_instruction = system_instruction

        response = self._client.models.generate_content(
            model=settings.generation_model,
            contents=prompt,
            config=config,
        )
        return response.text

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        response = self._client.models.embed_content(
            model=self._embedding_model,
            contents=text,
        )
        return response.embeddings[0].values

    async def generate_query_embedding(self, query: str) -> list[float]:
        """Generate an embedding vector optimized for queries.

        Args:
            query: Query text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        response = self._client.models.embed_content(
            model=self._embedding_model,
            contents=query,
        )
        return response.embeddings[0].values


@lru_cache
def get_gemini_client() -> GeminiClient:
    """Get cached Gemini client instance."""
    return GeminiClient()


# Singleton client instance
gemini_client = get_gemini_client()
