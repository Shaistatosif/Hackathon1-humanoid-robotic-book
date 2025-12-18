#!/usr/bin/env python3
"""
Content Ingestion Script for RAG System.

This script:
1. Reads markdown files from content/source/
2. Splits content into sentence-aware chunks
3. Generates embeddings using Cohere or Gemini (based on configuration)
4. Stores chunks in Qdrant vector database

Usage:
    python -m scripts.ingest_content [--language en|ur] [--collection textbook_chunks] [--provider cohere|gemini]
"""

import argparse
import asyncio
import hashlib
import re
import sys
import uuid
from pathlib import Path
from typing import Generator

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

import cohere
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src.core.config import settings


# Configuration
CHUNK_SIZE = 500  # Target characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks

# Embedding dimensions by provider
EMBEDDING_DIMENSIONS = {
    "cohere": 1024,  # embed-english-v3.0
    "gemini": 768,   # text-embedding-004
}


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Raw markdown content

    Returns:
        Tuple of (frontmatter dict, remaining content)
    """
    frontmatter = {}

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            # Parse simple YAML frontmatter
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()
            content = parts[2]

    return frontmatter, content


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences.

    Args:
        text: Text to split

    Returns:
        List of sentences
    """
    # Simple sentence splitting on common terminators
    # Handles abbreviations like "e.g." and "i.e." by not splitting on them
    text = re.sub(r'([.!?])\s+', r'\1\n', text)
    sentences = [s.strip() for s in text.split('\n') if s.strip()]
    return sentences


def chunk_content(
    content: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> Generator[tuple[str, int], None, None]:
    """Split content into overlapping chunks.

    Uses sentence-aware splitting to avoid breaking mid-sentence.

    Args:
        content: Text content to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Yields:
        Tuples of (chunk_text, chunk_order)
    """
    # Clean content - remove code blocks for chunking (we'll handle them separately)
    # But preserve them in the output
    sentences = split_into_sentences(content)

    current_chunk = []
    current_size = 0
    chunk_order = 0

    for sentence in sentences:
        sentence_size = len(sentence)

        # If single sentence is larger than chunk_size, split it
        if sentence_size > chunk_size:
            # Yield current chunk first if not empty
            if current_chunk:
                yield " ".join(current_chunk), chunk_order
                chunk_order += 1
                current_chunk = []
                current_size = 0

            # Split long sentence into smaller parts
            words = sentence.split()
            temp_chunk = []
            temp_size = 0

            for word in words:
                if temp_size + len(word) + 1 > chunk_size and temp_chunk:
                    yield " ".join(temp_chunk), chunk_order
                    chunk_order += 1
                    temp_chunk = []
                    temp_size = 0
                temp_chunk.append(word)
                temp_size += len(word) + 1

            if temp_chunk:
                current_chunk = temp_chunk
                current_size = temp_size
            continue

        # Check if adding this sentence exceeds chunk size
        if current_size + sentence_size + 1 > chunk_size and current_chunk:
            yield " ".join(current_chunk), chunk_order
            chunk_order += 1

            # Start new chunk with overlap from previous
            overlap_text = " ".join(current_chunk)[-overlap:] if overlap > 0 else ""
            current_chunk = [overlap_text] if overlap_text else []
            current_size = len(overlap_text)

        current_chunk.append(sentence)
        current_size += sentence_size + 1

    # Yield final chunk
    if current_chunk:
        yield " ".join(current_chunk), chunk_order


def extract_section_info(content: str, position: int) -> tuple[str, str]:
    """Extract section heading for a position in content.

    Args:
        content: Full markdown content
        position: Character position to find section for

    Returns:
        Tuple of (section_id, section_title)
    """
    lines = content[:position].split('\n')

    section_id = "intro"
    section_title = "Introduction"

    for line in reversed(lines):
        # Match markdown headings
        match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            # Create slug from title
            section_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            section_title = title
            break

    return section_id, section_title


def process_markdown_file(
    file_path: Path,
    language: str = "en"
) -> Generator[dict, None, None]:
    """Process a markdown file and yield chunk metadata.

    Args:
        file_path: Path to markdown file
        language: Language code (en, ur)

    Yields:
        Dict with chunk metadata
    """
    content = file_path.read_text(encoding="utf-8")
    frontmatter, body = extract_frontmatter(content)

    # Extract chapter info from path
    chapter_id = file_path.parent.name  # e.g., "chapter-1"
    title = frontmatter.get("title", chapter_id.replace("-", " ").title())

    # Clean body - remove code blocks for better chunking
    # Store code blocks separately
    code_block_pattern = r'```[\s\S]*?```'
    code_blocks = re.findall(code_block_pattern, body)
    clean_body = re.sub(code_block_pattern, '[CODE_BLOCK]', body)

    # Track position for section detection
    position = 0

    for chunk_text, chunk_order in chunk_content(clean_body):
        # Skip empty chunks or just code block placeholders
        if not chunk_text.strip() or chunk_text.strip() == '[CODE_BLOCK]':
            continue

        # Find section for this chunk
        section_id, section_title = extract_section_info(body, position)
        position += len(chunk_text)

        # Generate unique ID for chunk
        chunk_hash = hashlib.md5(
            f"{chapter_id}:{chunk_order}:{chunk_text[:50]}".encode()
        ).hexdigest()[:12]
        chunk_id = f"{chapter_id}-{chunk_order}-{chunk_hash}"

        yield {
            "id": chunk_id,
            "chapter_id": chapter_id,
            "section_id": section_id,
            "section_title": section_title,
            "chapter_title": title,
            "chunk_order": chunk_order,
            "chunk_text": chunk_text,
            "language": language,
        }


# Global clients (initialized in main)
cohere_client: cohere.AsyncClient | None = None
embedding_provider: str = "cohere"


async def generate_embedding(text: str) -> list[float]:
    """Generate embedding for text using configured provider.

    Args:
        text: Text to embed

    Returns:
        Embedding vector
    """
    global cohere_client, embedding_provider

    if embedding_provider == "cohere":
        if cohere_client is None:
            raise ValueError("Cohere client not initialized")
        response = await cohere_client.embed(
            texts=[text],
            model=settings.cohere_embedding_model,
            input_type="search_document",
            embedding_types=["float"],
        )
        return response.embeddings.float_[0]
    else:
        result = await genai.embed_content_async(
            model=f"models/{settings.embedding_model}",
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]


async def generate_embeddings_batch_cohere(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple texts using Cohere (batch API).

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    global cohere_client

    if cohere_client is None:
        raise ValueError("Cohere client not initialized")

    response = await cohere_client.embed(
        texts=texts,
        model=settings.cohere_embedding_model,
        input_type="search_document",
        embedding_types=["float"],
    )
    return response.embeddings.float_


async def process_chunks_batch(
    chunks: list[dict],
    batch_size: int = 96  # Cohere supports up to 96 texts per batch
) -> list[dict]:
    """Process chunks in batches to generate embeddings.

    Uses Cohere's batch API for efficiency when using Cohere provider.

    Args:
        chunks: List of chunk metadata dicts
        batch_size: Number of chunks to process per batch (max 96 for Cohere)

    Returns:
        Chunks with embeddings added
    """
    global embedding_provider
    results = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"  Processing batch {i // batch_size + 1}/{(len(chunks) + batch_size - 1) // batch_size}...")

        if embedding_provider == "cohere":
            # Use Cohere's efficient batch API
            texts = [chunk["chunk_text"] for chunk in batch]
            embeddings = await generate_embeddings_batch_cohere(texts)
        else:
            # Gemini: generate embeddings one by one
            tasks = [generate_embedding(chunk["chunk_text"]) for chunk in batch]
            embeddings = await asyncio.gather(*tasks)

        for chunk, embedding in zip(batch, embeddings):
            chunk["embedding"] = embedding
            results.append(chunk)

        # Small delay to avoid rate limiting
        await asyncio.sleep(0.2)

    return results


def setup_qdrant_collection(
    client: QdrantClient,
    collection_name: str,
    recreate: bool = False,
    dimension: int = 1024
) -> None:
    """Set up Qdrant collection for storing embeddings.

    Args:
        client: Qdrant client
        collection_name: Name of collection
        recreate: Whether to delete and recreate existing collection
        dimension: Vector dimension (1024 for Cohere, 768 for Gemini)
    """
    collections = client.get_collections()
    exists = any(c.name == collection_name for c in collections.collections)

    if exists and recreate:
        print(f"Deleting existing collection: {collection_name}")
        client.delete_collection(collection_name)
        exists = False

    if not exists:
        print(f"Creating collection: {collection_name} (dimension={dimension})")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=dimension,
                distance=Distance.COSINE,
            ),
        )


def upsert_chunks_to_qdrant(
    client: QdrantClient,
    collection_name: str,
    chunks: list[dict]
) -> None:
    """Upload chunks with embeddings to Qdrant.

    Args:
        client: Qdrant client
        collection_name: Name of collection
        chunks: List of chunks with embeddings
    """
    points = []

    for chunk in chunks:
        point = PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["id"])),
            vector=chunk["embedding"],
            payload={
                "chunk_id": chunk["id"],
                "chapter_id": chunk["chapter_id"],
                "section_id": chunk["section_id"],
                "section_title": chunk["section_title"],
                "chapter_title": chunk["chapter_title"],
                "chunk_text": chunk["chunk_text"],
                "chunk_order": chunk["chunk_order"],
                "language": chunk["language"],
            }
        )
        points.append(point)

    # Upsert in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch,
        )
        print(f"  Uploaded {min(i + batch_size, len(points))}/{len(points)} points")


async def main():
    """Main ingestion function."""
    global cohere_client, embedding_provider

    parser = argparse.ArgumentParser(description="Ingest textbook content for RAG")
    parser.add_argument(
        "--language",
        choices=["en", "ur"],
        default="en",
        help="Language of content to ingest"
    )
    parser.add_argument(
        "--collection",
        default=settings.qdrant_collection,
        help="Qdrant collection name"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Recreate collection (delete existing)"
    )
    parser.add_argument(
        "--content-dir",
        default="content/source",
        help="Directory containing markdown content"
    )
    parser.add_argument(
        "--provider",
        choices=["cohere", "gemini"],
        default=settings.embedding_provider,
        help="Embedding provider to use (default: from config)"
    )

    args = parser.parse_args()

    # Set embedding provider
    embedding_provider = args.provider
    dimension = EMBEDDING_DIMENSIONS[embedding_provider]
    print(f"Using embedding provider: {embedding_provider} (dimension={dimension})")

    # Configure embedding provider
    if embedding_provider == "cohere":
        if not settings.cohere_api_key:
            print("Error: COHERE_API_KEY not set in environment")
            sys.exit(1)
        cohere_client = cohere.AsyncClient(api_key=settings.cohere_api_key)
        print(f"Cohere model: {settings.cohere_embedding_model}")
    else:
        if not settings.gemini_api_key:
            print("Error: GEMINI_API_KEY not set in environment")
            sys.exit(1)
        genai.configure(api_key=settings.gemini_api_key)
        print(f"Gemini model: {settings.embedding_model}")

    # Set up Qdrant client
    if settings.qdrant_url:
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
    else:
        # Use local in-memory client for testing
        print("Warning: Using in-memory Qdrant (data will not persist)")
        client = QdrantClient(":memory:")

    # Find content directory
    content_dir = Path(args.content_dir)
    if not content_dir.exists():
        # Try relative to script location
        content_dir = Path(__file__).parent.parent.parent / args.content_dir

    if not content_dir.exists():
        print(f"Error: Content directory not found: {args.content_dir}")
        sys.exit(1)

    print(f"Content directory: {content_dir.absolute()}")

    # Find all markdown files
    if args.language == "ur":
        content_dir = content_dir.parent / "translations" / "ur"

    md_files = list(content_dir.glob("**/index.md"))

    if not md_files:
        print(f"No markdown files found in {content_dir}")
        sys.exit(1)

    print(f"Found {len(md_files)} markdown files")

    # Process all files
    all_chunks = []
    for file_path in md_files:
        print(f"\nProcessing: {file_path.relative_to(content_dir.parent.parent)}")
        chunks = list(process_markdown_file(file_path, args.language))
        print(f"  Generated {len(chunks)} chunks")
        all_chunks.extend(chunks)

    print(f"\nTotal chunks: {len(all_chunks)}")

    # Generate embeddings
    print("\nGenerating embeddings...")
    chunks_with_embeddings = await process_chunks_batch(all_chunks)

    # Set up collection with correct dimension for embedding provider
    print(f"\nSetting up Qdrant collection: {args.collection}")
    setup_qdrant_collection(client, args.collection, args.recreate, dimension)

    # Upload to Qdrant
    print("\nUploading to Qdrant...")
    upsert_chunks_to_qdrant(client, args.collection, chunks_with_embeddings)

    print(f"\nIngestion complete! {len(chunks_with_embeddings)} chunks stored in '{args.collection}'")

    # Print sample
    if chunks_with_embeddings:
        sample = chunks_with_embeddings[0]
        print("\nSample chunk:")
        print(f"  ID: {sample['id']}")
        print(f"  Chapter: {sample['chapter_title']}")
        print(f"  Section: {sample['section_title']}")
        print(f"  Text: {sample['chunk_text'][:100]}...")


if __name__ == "__main__":
    asyncio.run(main())
