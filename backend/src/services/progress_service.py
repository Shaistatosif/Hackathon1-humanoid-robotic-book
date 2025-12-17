"""Progress service for tracking reading progress and generating recommendations.

Handles user learning progress, bookmarks, and personalized recommendations.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.progress import Bookmark, ProgressStatus, ReadingProgress
from src.models.quiz import QuizAttempt


class ProgressService:
    """Service for managing user progress and recommendations."""

    def __init__(self, session: AsyncSession):
        """Initialize progress service.

        Args:
            session: Async database session.
        """
        self.session = session

    # ==================== Reading Progress ====================

    async def get_progress(self, user_id: str, chapter_id: str) -> ReadingProgress | None:
        """Get reading progress for a specific chapter.

        Args:
            user_id: User identifier.
            chapter_id: Chapter identifier.

        Returns:
            ReadingProgress or None if not found.
        """
        result = await self.session.execute(
            select(ReadingProgress).where(
                ReadingProgress.user_id == user_id,
                ReadingProgress.chapter_id == chapter_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_progress(self, user_id: str) -> list[ReadingProgress]:
        """Get all reading progress for a user.

        Args:
            user_id: User identifier.

        Returns:
            List of ReadingProgress records.
        """
        result = await self.session.execute(
            select(ReadingProgress)
            .where(ReadingProgress.user_id == user_id)
            .order_by(ReadingProgress.updated_at.desc())
        )
        return list(result.scalars().all())

    async def update_progress(
        self,
        user_id: str,
        chapter_id: str,
        progress_percent: float,
        time_spent_seconds: int = 0,
        last_position: float = 0.0,
    ) -> ReadingProgress:
        """Update or create reading progress for a chapter.

        Args:
            user_id: User identifier.
            chapter_id: Chapter identifier.
            progress_percent: Percentage completed (0-100).
            time_spent_seconds: Additional time spent reading.
            last_position: Current scroll position.

        Returns:
            Updated ReadingProgress record.
        """
        progress = await self.get_progress(user_id, chapter_id)

        if not progress:
            # Create new progress record
            progress = ReadingProgress(
                user_id=user_id,
                chapter_id=chapter_id,
                status=ProgressStatus.IN_PROGRESS,
                progress_percent=progress_percent,
                time_spent_seconds=time_spent_seconds,
                last_position=last_position,
                started_at=datetime.utcnow(),
            )
            self.session.add(progress)
        else:
            # Update existing progress
            progress.progress_percent = max(progress.progress_percent, progress_percent)
            progress.time_spent_seconds += time_spent_seconds
            progress.last_position = last_position

            # Update status based on progress
            if progress.progress_percent >= 90:
                progress.status = ProgressStatus.COMPLETED
                if not progress.completed_at:
                    progress.completed_at = datetime.utcnow()
            elif progress.progress_percent > 0:
                progress.status = ProgressStatus.IN_PROGRESS

        await self.session.commit()
        await self.session.refresh(progress)
        return progress

    async def mark_completed(self, user_id: str, chapter_id: str) -> ReadingProgress:
        """Mark a chapter as completed.

        Args:
            user_id: User identifier.
            chapter_id: Chapter identifier.

        Returns:
            Updated ReadingProgress record.
        """
        return await self.update_progress(user_id, chapter_id, 100.0)

    # ==================== Bookmarks ====================

    async def get_bookmarks(self, user_id: str) -> list[Bookmark]:
        """Get all bookmarks for a user.

        Args:
            user_id: User identifier.

        Returns:
            List of Bookmark records.
        """
        result = await self.session.execute(
            select(Bookmark)
            .where(Bookmark.user_id == user_id)
            .order_by(Bookmark.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_bookmark(
        self, user_id: str, chapter_id: str, section_id: str | None = None
    ) -> Bookmark | None:
        """Get a specific bookmark.

        Args:
            user_id: User identifier.
            chapter_id: Chapter identifier.
            section_id: Optional section identifier.

        Returns:
            Bookmark or None if not found.
        """
        query = select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.chapter_id == chapter_id,
        )
        if section_id:
            query = query.where(Bookmark.section_id == section_id)
        else:
            query = query.where(Bookmark.section_id.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_bookmark(
        self,
        user_id: str,
        chapter_id: str,
        title: str,
        section_id: str | None = None,
        note: str | None = None,
        position: float = 0.0,
    ) -> Bookmark:
        """Create a new bookmark.

        Args:
            user_id: User identifier.
            chapter_id: Chapter identifier.
            title: Bookmark title.
            section_id: Optional section anchor.
            note: Optional user note.
            position: Scroll position.

        Returns:
            Created Bookmark record.
        """
        # Check if bookmark already exists
        existing = await self.get_bookmark(user_id, chapter_id, section_id)
        if existing:
            # Update existing bookmark
            existing.title = title
            existing.note = note
            existing.position = position
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        bookmark = Bookmark(
            user_id=user_id,
            chapter_id=chapter_id,
            section_id=section_id,
            title=title,
            note=note,
            position=position,
        )
        self.session.add(bookmark)
        await self.session.commit()
        await self.session.refresh(bookmark)
        return bookmark

    async def delete_bookmark(self, user_id: str, bookmark_id: str) -> bool:
        """Delete a bookmark.

        Args:
            user_id: User identifier.
            bookmark_id: Bookmark identifier.

        Returns:
            True if deleted, False if not found.
        """
        result = await self.session.execute(
            select(Bookmark).where(
                Bookmark.id == bookmark_id,
                Bookmark.user_id == user_id,
            )
        )
        bookmark = result.scalar_one_or_none()

        if not bookmark:
            return False

        await self.session.delete(bookmark)
        await self.session.commit()
        return True

    # ==================== Dashboard & Recommendations ====================

    async def get_dashboard_data(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive dashboard data for a user.

        Args:
            user_id: User identifier.

        Returns:
            Dashboard data including progress, stats, and recommendations.
        """
        # Get all progress
        progress_list = await self.get_all_progress(user_id)

        # Get bookmarks
        bookmarks = await self.get_bookmarks(user_id)

        # Get quiz history
        quiz_result = await self.session.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.completed_at.desc())
            .limit(10)
        )
        quiz_attempts = list(quiz_result.scalars().all())

        # Calculate stats
        completed_chapters = sum(
            1 for p in progress_list if p.status == ProgressStatus.COMPLETED
        )
        in_progress_chapters = sum(
            1 for p in progress_list if p.status == ProgressStatus.IN_PROGRESS
        )
        total_time_seconds = sum(p.time_spent_seconds for p in progress_list)

        # Calculate average quiz score
        avg_quiz_score = 0.0
        completed_quizzes = [a for a in quiz_attempts if a.score is not None]
        if completed_quizzes:
            scores = [a.score for a in completed_quizzes if a.score is not None]
            avg_quiz_score = sum(scores) / len(scores) if scores else 0.0

        # Generate recommendations
        recommendations = await self._generate_recommendations(
            user_id, progress_list, quiz_attempts
        )

        return {
            "progress": [
                {
                    "chapter_id": p.chapter_id,
                    "status": p.status,
                    "progress_percent": p.progress_percent,
                    "time_spent_seconds": p.time_spent_seconds,
                    "last_position": p.last_position,
                    "started_at": p.started_at.isoformat() if p.started_at else None,
                    "completed_at": p.completed_at.isoformat() if p.completed_at else None,
                }
                for p in progress_list
            ],
            "bookmarks": [
                {
                    "id": b.id,
                    "chapter_id": b.chapter_id,
                    "section_id": b.section_id,
                    "title": b.title,
                    "note": b.note,
                    "created_at": b.created_at.isoformat(),
                }
                for b in bookmarks
            ],
            "quiz_history": [
                {
                    "id": a.id,
                    "quiz_id": a.quiz_id,
                    "score": a.score or 0,
                    "total_questions": 5,  # Default quiz length
                    "correct_answers": int((a.score or 0) / 100 * 5),  # Calculated from score
                    "completed_at": a.completed_at.isoformat() if a.completed_at else None,
                }
                for a in quiz_attempts
            ],
            "stats": {
                "completed_chapters": completed_chapters,
                "in_progress_chapters": in_progress_chapters,
                "total_time_minutes": total_time_seconds // 60,
                "total_bookmarks": len(bookmarks),
                "quizzes_taken": len(quiz_attempts),
                "average_quiz_score": round(avg_quiz_score, 1),
            },
            "recommendations": recommendations,
        }

    async def _generate_recommendations(
        self,
        user_id: str,
        progress_list: list[ReadingProgress],
        quiz_attempts: list[QuizAttempt],
    ) -> list[dict[str, Any]]:
        """Generate personalized learning recommendations.

        Args:
            user_id: User identifier.
            progress_list: User's reading progress.
            quiz_attempts: User's quiz history.

        Returns:
            List of recommendation objects.
        """
        recommendations = []

        # Build sets for quick lookup
        completed_chapters = {
            p.chapter_id for p in progress_list if p.status == ProgressStatus.COMPLETED
        }
        in_progress_chapters = {
            p.chapter_id for p in progress_list if p.status == ProgressStatus.IN_PROGRESS
        }
        chapters_with_quiz = {a.quiz_id.replace("-quiz", "") for a in quiz_attempts if a.quiz_id}

        # Define chapter order
        all_chapters = ["chapter-1", "chapter-2", "chapter-3"]

        # Recommendation 1: Continue in-progress chapter
        for chapter_id in in_progress_chapters:
            progress = next(p for p in progress_list if p.chapter_id == chapter_id)
            recommendations.append({
                "type": "continue",
                "chapter_id": chapter_id,
                "title": "Continue reading",
                "description": f"You're {progress.progress_percent:.0f}% through this chapter. Keep going!",
                "priority": 1,
            })

        # Recommendation 2: Start next chapter
        for chapter_id in all_chapters:
            if chapter_id not in completed_chapters and chapter_id not in in_progress_chapters:
                recommendations.append({
                    "type": "start",
                    "chapter_id": chapter_id,
                    "title": "Start new chapter",
                    "description": "Begin learning new concepts in this chapter.",
                    "priority": 2,
                })
                break  # Only suggest one new chapter

        # Recommendation 3: Take quiz for completed chapters
        for chapter_id in completed_chapters:
            if chapter_id not in chapters_with_quiz:
                recommendations.append({
                    "type": "quiz",
                    "chapter_id": chapter_id,
                    "title": "Take chapter quiz",
                    "description": "Test your understanding with a quiz.",
                    "priority": 3,
                })

        # Recommendation 4: Retry failed quizzes
        for attempt in quiz_attempts:
            score = attempt.score if attempt.score is not None else 0.0
            if score < 70:
                retry_chapter_id = attempt.quiz_id.replace("-quiz", "") if attempt.quiz_id else None
                if retry_chapter_id:
                    recommendations.append({
                        "type": "retry_quiz",
                        "chapter_id": retry_chapter_id,
                        "title": "Retry quiz",
                        "description": f"Your score was {score}%. Try again to improve!",
                        "priority": 4,
                    })
                    break  # Only suggest one retry

        # Sort by priority and limit
        def get_priority(rec: dict[str, Any]) -> int:
            return int(rec.get("priority", 999))
        recommendations.sort(key=get_priority)
        return recommendations[:5]

    async def get_completion_stats(self, user_id: str) -> dict[str, Any]:
        """Get overall completion statistics.

        Args:
            user_id: User identifier.

        Returns:
            Completion statistics.
        """
        progress_list = await self.get_all_progress(user_id)

        total_chapters = 3  # Hardcoded for now
        completed = sum(
            1 for p in progress_list if p.status == ProgressStatus.COMPLETED
        )

        return {
            "total_chapters": total_chapters,
            "completed_chapters": completed,
            "completion_percent": (completed / total_chapters * 100) if total_chapters > 0 else 0,
        }
