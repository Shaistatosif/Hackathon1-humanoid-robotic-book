"""Content API router for chapter summaries and metadata.

Provides endpoints for accessing chapter content, summaries, and related data.
"""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/content", tags=["content"])

# Path to summaries directory
SUMMARIES_DIR = Path(__file__).parent.parent.parent.parent / "content" / "summaries"


class KeyConcept(BaseModel):
    """A key concept from a chapter summary."""

    concept: str
    explanation: str


class ChapterSummary(BaseModel):
    """Chapter summary response model."""

    chapter_id: str
    title: str
    overview: str
    key_concepts: list[KeyConcept]
    takeaways: list[str]


class ChapterListItem(BaseModel):
    """Chapter list item for available summaries."""

    chapter_id: str
    title: str
    has_summary: bool


def load_summary(chapter_id: str) -> dict[str, Any] | None:
    """Load summary from JSON file.

    Args:
        chapter_id: Chapter identifier.

    Returns:
        Summary dict or None if not found.
    """
    file_path = SUMMARIES_DIR / f"{chapter_id}-summary.json"
    if not file_path.exists():
        return None

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def get_available_summaries() -> list[dict[str, Any]]:
    """Get list of available chapter summaries.

    Returns:
        List of chapter info dicts.
    """
    summaries = []
    if SUMMARIES_DIR.exists():
        for file_path in SUMMARIES_DIR.glob("*-summary.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    summaries.append({
                        "chapter_id": data.get("chapter_id"),
                        "title": data.get("title"),
                        "has_summary": True,
                    })
            except (json.JSONDecodeError, KeyError):
                continue

    return sorted(summaries, key=lambda x: x.get("chapter_id", ""))


@router.get("/summaries", response_model=list[ChapterListItem])
async def list_summaries() -> list[ChapterListItem]:
    """List all available chapter summaries.

    Returns:
        List of chapters with summary availability.
    """
    summaries = get_available_summaries()
    return [ChapterListItem(**s) for s in summaries]


@router.get("/summaries/{chapter_id}", response_model=ChapterSummary)
async def get_summary(chapter_id: str) -> ChapterSummary:
    """Get summary for a specific chapter.

    Args:
        chapter_id: Chapter identifier (e.g., "chapter-1").

    Returns:
        Chapter summary with overview, key concepts, and takeaways.

    Raises:
        HTTPException: If summary not found.
    """
    summary = load_summary(chapter_id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"Summary not found for chapter: {chapter_id}",
        )

    return ChapterSummary(**summary)


@router.get("/chapters")
async def list_chapters() -> list[dict[str, Any]]:
    """List all chapters with basic metadata.

    Returns:
        List of chapter metadata.
    """
    # For now, return chapters based on available summaries
    # In a full implementation, this would query the database
    chapters = [
        {
            "id": "chapter-1",
            "title": "Introduction to Humanoid Robotics",
            "slug": "chapter-1",
            "order": 1,
        },
        {
            "id": "chapter-2",
            "title": "Robot Components and Architecture",
            "slug": "chapter-2",
            "order": 2,
        },
        {
            "id": "chapter-3",
            "title": "Sensors and Actuators",
            "slug": "chapter-3",
            "order": 3,
        },
    ]
    return chapters
