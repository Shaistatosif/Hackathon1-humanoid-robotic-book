"""Qdrant vector database client singleton.

Provides a configured Qdrant client for vector similarity search operations.
"""

from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.core.config import settings


@lru_cache
def get_qdrant_client() -> QdrantClient:
    """Get cached Qdrant client instance.

    Returns:
        QdrantClient: Configured Qdrant client.

    Raises:
        ValueError: If Qdrant URL is not configured.
    """
    if not settings.qdrant_url:
        # Return a local in-memory client for development
        return QdrantClient(":memory:")

    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key if settings.qdrant_api_key else None,
        timeout=30,
    )


async def ensure_collection_exists(
    client: QdrantClient,
    collection_name: str | None = None,
    vector_size: int = 768,  # Gemini text-embedding-004 dimension
) -> None:
    """Ensure the vector collection exists, creating it if necessary.

    Args:
        client: Qdrant client instance.
        collection_name: Name of the collection. Defaults to config value.
        vector_size: Dimension of the embedding vectors.
    """
    name = collection_name or settings.qdrant_collection

    collections = client.get_collections()
    existing_names = [c.name for c in collections.collections]

    if name not in existing_names:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )


# Singleton client instance
qdrant_client = get_qdrant_client()
