"""User API router for dashboard, progress, and bookmarks.

Provides endpoints for user-specific data including reading progress,
bookmarks, quiz history, and personalized recommendations.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.services.progress_service import ProgressService

router = APIRouter(prefix="/user", tags=["user"])


# ==================== Request/Response Models ====================


class ProgressUpdateRequest(BaseModel):
    """Request to update reading progress."""

    chapter_id: str
    progress_percent: float
    time_spent_seconds: int = 0
    last_position: float = 0.0


class ProgressResponse(BaseModel):
    """Reading progress response."""

    chapter_id: str
    status: str
    progress_percent: float
    time_spent_seconds: int
    last_position: float
    started_at: str | None
    completed_at: str | None


class BookmarkCreateRequest(BaseModel):
    """Request to create a bookmark."""

    chapter_id: str
    title: str
    section_id: str | None = None
    note: str | None = None
    position: float = 0.0


class BookmarkResponse(BaseModel):
    """Bookmark response."""

    id: str
    chapter_id: str
    section_id: str | None
    title: str
    note: str | None
    position: float
    created_at: str


class DashboardStats(BaseModel):
    """Dashboard statistics."""

    completed_chapters: int
    in_progress_chapters: int
    total_time_minutes: int
    total_bookmarks: int
    quizzes_taken: int
    average_quiz_score: float


class RecommendationResponse(BaseModel):
    """Learning recommendation."""

    type: str
    chapter_id: str
    title: str
    description: str
    priority: int


class DashboardResponse(BaseModel):
    """Complete dashboard data response."""

    progress: list[dict[str, Any]]
    bookmarks: list[dict[str, Any]]
    quiz_history: list[dict[str, Any]]
    stats: DashboardStats
    recommendations: list[RecommendationResponse]


# ==================== Dashboard Endpoints ====================


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    """Get complete dashboard data for the authenticated user.

    Returns progress, bookmarks, quiz history, stats, and recommendations.
    """
    service = ProgressService(db)
    data = await service.get_dashboard_data(user.id)
    return DashboardResponse(**data)


@router.get("/stats")
async def get_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get completion statistics for the authenticated user."""
    service = ProgressService(db)
    return await service.get_completion_stats(user.id)


# ==================== Progress Endpoints ====================


@router.get("/progress", response_model=list[ProgressResponse])
async def get_all_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ProgressResponse]:
    """Get reading progress for all chapters."""
    service = ProgressService(db)
    progress_list = await service.get_all_progress(user.id)

    return [
        ProgressResponse(
            chapter_id=p.chapter_id,
            status=p.status,
            progress_percent=p.progress_percent,
            time_spent_seconds=p.time_spent_seconds,
            last_position=p.last_position,
            started_at=p.started_at.isoformat() if p.started_at else None,
            completed_at=p.completed_at.isoformat() if p.completed_at else None,
        )
        for p in progress_list
    ]


@router.get("/progress/{chapter_id}", response_model=ProgressResponse | None)
async def get_chapter_progress(
    chapter_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProgressResponse | None:
    """Get reading progress for a specific chapter."""
    service = ProgressService(db)
    progress = await service.get_progress(user.id, chapter_id)

    if not progress:
        return None

    return ProgressResponse(
        chapter_id=progress.chapter_id,
        status=progress.status,
        progress_percent=progress.progress_percent,
        time_spent_seconds=progress.time_spent_seconds,
        last_position=progress.last_position,
        started_at=progress.started_at.isoformat() if progress.started_at else None,
        completed_at=progress.completed_at.isoformat() if progress.completed_at else None,
    )


@router.post("/progress", response_model=ProgressResponse)
async def update_progress(
    request: ProgressUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProgressResponse:
    """Update reading progress for a chapter."""
    service = ProgressService(db)
    progress = await service.update_progress(
        user_id=user.id,
        chapter_id=request.chapter_id,
        progress_percent=request.progress_percent,
        time_spent_seconds=request.time_spent_seconds,
        last_position=request.last_position,
    )

    return ProgressResponse(
        chapter_id=progress.chapter_id,
        status=progress.status,
        progress_percent=progress.progress_percent,
        time_spent_seconds=progress.time_spent_seconds,
        last_position=progress.last_position,
        started_at=progress.started_at.isoformat() if progress.started_at else None,
        completed_at=progress.completed_at.isoformat() if progress.completed_at else None,
    )


@router.post("/progress/{chapter_id}/complete", response_model=ProgressResponse)
async def mark_chapter_complete(
    chapter_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProgressResponse:
    """Mark a chapter as completed."""
    service = ProgressService(db)
    progress = await service.mark_completed(user.id, chapter_id)

    return ProgressResponse(
        chapter_id=progress.chapter_id,
        status=progress.status,
        progress_percent=progress.progress_percent,
        time_spent_seconds=progress.time_spent_seconds,
        last_position=progress.last_position,
        started_at=progress.started_at.isoformat() if progress.started_at else None,
        completed_at=progress.completed_at.isoformat() if progress.completed_at else None,
    )


# ==================== Bookmark Endpoints ====================


@router.get("/bookmarks", response_model=list[BookmarkResponse])
async def get_bookmarks(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BookmarkResponse]:
    """Get all bookmarks for the authenticated user."""
    service = ProgressService(db)
    bookmarks = await service.get_bookmarks(user.id)

    return [
        BookmarkResponse(
            id=b.id,
            chapter_id=b.chapter_id,
            section_id=b.section_id,
            title=b.title,
            note=b.note,
            position=b.position,
            created_at=b.created_at.isoformat(),
        )
        for b in bookmarks
    ]


@router.post("/bookmarks", response_model=BookmarkResponse)
async def create_bookmark(
    request: BookmarkCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookmarkResponse:
    """Create a new bookmark."""
    service = ProgressService(db)
    bookmark = await service.create_bookmark(
        user_id=user.id,
        chapter_id=request.chapter_id,
        title=request.title,
        section_id=request.section_id,
        note=request.note,
        position=request.position,
    )

    return BookmarkResponse(
        id=bookmark.id,
        chapter_id=bookmark.chapter_id,
        section_id=bookmark.section_id,
        title=bookmark.title,
        note=bookmark.note,
        position=bookmark.position,
        created_at=bookmark.created_at.isoformat(),
    )


@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Delete a bookmark."""
    service = ProgressService(db)
    deleted = await service.delete_bookmark(user.id, bookmark_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    return {"deleted": True}


# ==================== Recommendations Endpoint ====================


@router.get("/recommendations", response_model=list[RecommendationResponse])
async def get_recommendations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[RecommendationResponse]:
    """Get personalized learning recommendations."""
    service = ProgressService(db)
    data = await service.get_dashboard_data(user.id)

    return [RecommendationResponse(**r) for r in data["recommendations"]]
