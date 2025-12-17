"""Gemini API client wrapper.

Provides text embedding and generation capabilities using Google's Gemini API.
"""

from functools import lru_cache

import google.generativeai as genai

from src.core.config import settings


@lru_cache
def configure_gemini() -> None:
    """Configure the Gemini API with the API key."""
    if settings.gemini_api_key:
        genai.configure(api_key=settings.gemini_api_key)


class GeminiClient:
    """Wrapper for Gemini API operations."""

    def __init__(self) -> None:
        """Initialize the Gemini client."""
        configure_gemini()
        self._generation_model: genai.GenerativeModel | None = None
        self._embedding_model = settings.embedding_model

    @property
    def generation_model(self) -> genai.GenerativeModel:
        """Get or create the generation model instance."""
        if self._generation_model is None:
            self._generation_model = genai.GenerativeModel(
                model_name=settings.generation_model,
                generation_config=genai.GenerationConfig(
                    temperature=settings.generation_temperature,
                ),
            )
        return self._generation_model

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
        model = self.generation_model
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=settings.generation_model,
                generation_config=genai.GenerationConfig(
                    temperature=settings.generation_temperature,
                ),
                system_instruction=system_instruction,
            )

        response = await model.generate_content_async(prompt)
        return response.text

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        result = await genai.embed_content_async(
            model=f"models/{self._embedding_model}",
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]

    async def generate_query_embedding(self, query: str) -> list[float]:
        """Generate an embedding vector optimized for queries.

        Args:
            query: Query text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        result = await genai.embed_content_async(
            model=f"models/{self._embedding_model}",
            content=query,
            task_type="retrieval_query",
        )
        return result["embedding"]


@lru_cache
def get_gemini_client() -> GeminiClient:
    """Get cached Gemini client instance."""
    return GeminiClient()


# Singleton client instance
gemini_client = get_gemini_client()
