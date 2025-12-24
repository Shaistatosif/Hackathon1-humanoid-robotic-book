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
    """
    # If cloud URL is provided, use cloud
    if settings.qdrant_url:
        return QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None,
            timeout=30,
        )

    # Otherwise use local persistent storage
    from pathlib import Path
    qdrant_path = Path(settings.qdrant_path)
    qdrant_path.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(qdrant_path))


async def ensure_collection_exists(
    client: QdrantClient,
    collection_name: str | None = None,
    vector_size: int | None = None,
) -> None:
    """Ensure the vector collection exists, creating it if necessary.

    Args:
        client: Qdrant client instance.
        collection_name: Name of the collection. Defaults to config value.
        vector_size: Dimension of the embedding vectors. Defaults to configured provider dimension.
    """
    name = collection_name or settings.qdrant_collection
    size = vector_size if vector_size is not None else settings.embedding_dimension

    collections = client.get_collections()
    existing_names = [c.name for c in collections.collections]

    if name not in existing_names:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=size,
                distance=Distance.COSINE,
            ),
        )


# Singleton client instance
qdrant_client = get_qdrant_client()
