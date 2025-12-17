"""Quiz Service for chapter assessments.

Provides quiz management, attempt tracking, and answer scoring.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.quiz import Question, QuestionType, Quiz, QuizAttempt


@dataclass
class QuizSummary:
    """Summary of a quiz."""

    id: str
    chapter_id: str
    title: str
    description: str | None
    question_count: int
    passing_score: int
    time_limit_minutes: int | None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "chapter_id": self.chapter_id,
            "title": self.title,
            "description": self.description,
            "question_count": self.question_count,
            "passing_score": self.passing_score,
            "time_limit_minutes": self.time_limit_minutes,
        }


@dataclass
class QuestionData:
    """Question data for display (without correct answer)."""

    id: str
    question_type: str
    question_text: str
    options: list[str] | None
    points: int
    order: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "question_type": self.question_type,
            "question_text": self.question_text,
            "options": self.options,
            "points": self.points,
            "order": self.order,
        }


@dataclass
class AnswerResult:
    """Result for a single answer."""

    question_id: str
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str | None
    points_earned: int
    points_possible: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "question_text": self.question_text,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "is_correct": self.is_correct,
            "explanation": self.explanation,
            "points_earned": self.points_earned,
            "points_possible": self.points_possible,
        }


@dataclass
class QuizResult:
    """Complete quiz result."""

    attempt_id: str
    quiz_id: str
    score: float
    passed: bool
    total_points: int
    earned_points: int
    time_taken_seconds: int | None
    answers: list[AnswerResult]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "attempt_id": self.attempt_id,
            "quiz_id": self.quiz_id,
            "score": self.score,
            "passed": self.passed,
            "total_points": self.total_points,
            "earned_points": self.earned_points,
            "time_taken_seconds": self.time_taken_seconds,
            "answers": [a.to_dict() for a in self.answers],
        }


class QuizService:
    """Service for quiz operations."""

    def __init__(self, db: AsyncSession):
        """Initialize quiz service.

        Args:
            db: Async database session
        """
        self.db = db
        self._quiz_cache: dict[str, dict] = {}

    async def load_quiz_from_file(self, chapter_id: str) -> dict | None:
        """Load quiz data from JSON file.

        Args:
            chapter_id: Chapter identifier (e.g., "chapter-1")

        Returns:
            Quiz data dictionary or None
        """
        if chapter_id in self._quiz_cache:
            return self._quiz_cache[chapter_id]

        # Try multiple paths
        quiz_paths = [
            Path(f"content/quizzes/{chapter_id}-quiz.json"),
            Path(__file__).parent.parent.parent.parent / f"content/quizzes/{chapter_id}-quiz.json",
        ]

        for quiz_path in quiz_paths:
            if quiz_path.exists():
                try:
                    quiz_data = json.loads(quiz_path.read_text(encoding='utf-8'))
                    self._quiz_cache[chapter_id] = quiz_data
                    return quiz_data
                except (json.JSONDecodeError, IOError):
                    continue

        return None

    async def get_quiz_for_chapter(self, chapter_id: str) -> QuizSummary | None:
        """Get quiz summary for a chapter.

        Args:
            chapter_id: Chapter identifier

        Returns:
            QuizSummary or None if no quiz exists
        """
        # First try database
        result = await self.db.execute(
            select(Quiz)
            .where(Quiz.chapter_id == chapter_id)
            .where(Quiz.is_active == True)
            .options(selectinload(Quiz.questions))
        )
        quiz = result.scalar_one_or_none()

        if quiz:
            return QuizSummary(
                id=quiz.id,
                chapter_id=quiz.chapter_id,
                title=quiz.title,
                description=quiz.description,
                question_count=len(quiz.questions),
                passing_score=quiz.passing_score,
                time_limit_minutes=quiz.time_limit_minutes,
            )

        # Fall back to file-based quiz
        quiz_data = await self.load_quiz_from_file(chapter_id)
        if quiz_data:
            return QuizSummary(
                id=quiz_data.get("id", f"quiz-{chapter_id}"),
                chapter_id=chapter_id,
                title=quiz_data.get("title", f"Quiz: {chapter_id}"),
                description=quiz_data.get("description"),
                question_count=len(quiz_data.get("questions", [])),
                passing_score=70,
                time_limit_minutes=None,
            )

        return None

    async def get_quiz_questions(self, chapter_id: str) -> list[QuestionData]:
        """Get quiz questions for display (without correct answers).

        Args:
            chapter_id: Chapter identifier

        Returns:
            List of QuestionData
        """
        # First try database
        result = await self.db.execute(
            select(Quiz)
            .where(Quiz.chapter_id == chapter_id)
            .where(Quiz.is_active == True)
            .options(selectinload(Quiz.questions))
        )
        quiz = result.scalar_one_or_none()

        if quiz:
            return [
                QuestionData(
                    id=q.id,
                    question_type=q.question_type.value if isinstance(q.question_type, QuestionType) else q.question_type,
                    question_text=q.question_text,
                    options=q.options,
                    points=q.points,
                    order=q.order,
                )
                for q in sorted(quiz.questions, key=lambda x: x.order)
            ]

        # Fall back to file-based quiz
        quiz_data = await self.load_quiz_from_file(chapter_id)
        if quiz_data:
            return [
                QuestionData(
                    id=q.get("id", str(i)),
                    question_type=q.get("type", "multiple_choice"),
                    question_text=q.get("question", ""),
                    options=q.get("options"),
                    points=q.get("points", 1),
                    order=q.get("order", i),
                )
                for i, q in enumerate(quiz_data.get("questions", []))
            ]

        return []

    async def start_attempt(
        self,
        chapter_id: str,
        user_id: str | None = None,
    ) -> QuizAttempt:
        """Start a new quiz attempt.

        Args:
            chapter_id: Chapter identifier
            user_id: Optional user ID

        Returns:
            New QuizAttempt
        """
        quiz_summary = await self.get_quiz_for_chapter(chapter_id)
        if not quiz_summary:
            raise ValueError(f"No quiz found for chapter: {chapter_id}")

        attempt = QuizAttempt(
            quiz_id=quiz_summary.id,
            user_id=user_id,
            started_at=datetime.utcnow(),
        )

        self.db.add(attempt)
        await self.db.commit()
        await self.db.refresh(attempt)

        return attempt

    def _normalize_answer(self, answer: str) -> str:
        """Normalize answer for comparison.

        Args:
            answer: User's answer

        Returns:
            Normalized answer string
        """
        # Strip whitespace and convert to lowercase
        normalized = answer.strip().lower()

        # For MCQ, extract just the letter if full option given
        if normalized and normalized[0] in 'abcd' and (len(normalized) == 1 or normalized[1] in '.):'):
            return normalized[0].upper()

        # For True/False
        if normalized in ('true', 't', 'yes', '1'):
            return 'True'
        if normalized in ('false', 'f', 'no', '0'):
            return 'False'

        return answer.strip()

    def _check_answer(
        self,
        user_answer: str,
        correct_answer: str,
        question_type: str,
    ) -> bool:
        """Check if user's answer is correct.

        Args:
            user_answer: User's submitted answer
            correct_answer: Correct answer
            question_type: Type of question

        Returns:
            True if answer is correct
        """
        user_normalized = self._normalize_answer(user_answer)
        correct_normalized = self._normalize_answer(correct_answer)

        if question_type in ('multiple_choice', 'true_false'):
            return user_normalized.upper() == correct_normalized.upper()

        # For short answer, do a more flexible comparison
        # In a production system, this could use NLP/semantic similarity
        user_words = set(user_normalized.lower().split())
        correct_words = set(correct_normalized.lower().split())

        # Check for significant word overlap (at least 50% of key words)
        if len(correct_words) > 0:
            overlap = len(user_words & correct_words)
            return overlap >= len(correct_words) * 0.5

        return user_normalized.lower() == correct_normalized.lower()

    async def submit_answers(
        self,
        attempt_id: str,
        answers: dict[str, str],
    ) -> QuizResult:
        """Submit quiz answers and calculate score.

        Args:
            attempt_id: Quiz attempt ID
            answers: Dictionary of {question_id: user_answer}

        Returns:
            QuizResult with scoring
        """
        # Get attempt
        result = await self.db.execute(
            select(QuizAttempt).where(QuizAttempt.id == attempt_id)
        )
        attempt = result.scalar_one_or_none()

        if not attempt:
            raise ValueError(f"Attempt not found: {attempt_id}")

        if attempt.is_complete:
            raise ValueError("Attempt already completed")

        # Get quiz data
        quiz_id = attempt.quiz_id

        # Try database first
        db_result = await self.db.execute(
            select(Quiz)
            .where(Quiz.id == quiz_id)
            .options(selectinload(Quiz.questions))
        )
        quiz = db_result.scalar_one_or_none()

        questions_data = []
        passing_score = 70

        if quiz:
            passing_score = quiz.passing_score
            for q in quiz.questions:
                questions_data.append({
                    "id": q.id,
                    "type": q.question_type.value if isinstance(q.question_type, QuestionType) else q.question_type,
                    "question": q.question_text,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                    "points": q.points,
                })
        else:
            # Try file-based quiz
            # Extract chapter_id from quiz_id
            chapter_id = quiz_id.replace("quiz-", "").split("-")[0:2]
            chapter_id = "-".join(chapter_id) if len(chapter_id) > 1 else chapter_id[0]

            quiz_data = await self.load_quiz_from_file(chapter_id)
            if not quiz_data:
                # Try with the quiz_id as chapter_id
                for ch in ["chapter-1", "chapter-2", "chapter-3"]:
                    quiz_data = await self.load_quiz_from_file(ch)
                    if quiz_data and quiz_data.get("id") == quiz_id:
                        break

            if quiz_data:
                for q in quiz_data.get("questions", []):
                    questions_data.append({
                        "id": q.get("id"),
                        "type": q.get("type", "multiple_choice"),
                        "question": q.get("question", ""),
                        "correct_answer": q.get("correct_answer", ""),
                        "explanation": q.get("explanation"),
                        "points": q.get("points", 1),
                    })

        # Score each answer
        answer_results = []
        total_points = 0
        earned_points = 0

        for q in questions_data:
            q_id = q["id"]
            user_answer = answers.get(q_id, "")
            correct_answer = q["correct_answer"]
            points = q["points"]

            is_correct = self._check_answer(
                user_answer,
                correct_answer,
                q["type"]
            )

            total_points += points
            if is_correct:
                earned_points += points

            answer_results.append(AnswerResult(
                question_id=q_id,
                question_text=q["question"],
                user_answer=user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
                explanation=q.get("explanation"),
                points_earned=points if is_correct else 0,
                points_possible=points,
            ))

        # Calculate score
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = score >= passing_score

        # Calculate time taken
        time_taken = None
        if attempt.started_at:
            time_taken = int((datetime.utcnow() - attempt.started_at).total_seconds())

        # Update attempt
        attempt.completed_at = datetime.utcnow()
        attempt.score = score
        attempt.passed = passed
        attempt.answers = answers
        attempt.time_taken_seconds = time_taken

        await self.db.commit()

        return QuizResult(
            attempt_id=attempt_id,
            quiz_id=quiz_id,
            score=score,
            passed=passed,
            total_points=total_points,
            earned_points=earned_points,
            time_taken_seconds=time_taken,
            answers=answer_results,
        )

    async def get_attempt_result(self, attempt_id: str) -> QuizResult | None:
        """Get result for a completed attempt.

        Args:
            attempt_id: Quiz attempt ID

        Returns:
            QuizResult or None
        """
        result = await self.db.execute(
            select(QuizAttempt).where(QuizAttempt.id == attempt_id)
        )
        attempt = result.scalar_one_or_none()

        if not attempt or not attempt.is_complete:
            return None

        # Reconstruct result from stored data
        # This is a simplified version - in production, store full results
        return QuizResult(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz_id,
            score=attempt.score or 0,
            passed=attempt.passed or False,
            total_points=0,  # Would need to recalculate
            earned_points=0,
            time_taken_seconds=attempt.time_taken_seconds,
            answers=[],  # Would need to reconstruct
        )

    async def get_user_attempts(
        self,
        user_id: str,
        chapter_id: str | None = None,
    ) -> list[dict]:
        """Get quiz attempts for a user.

        Args:
            user_id: User ID
            chapter_id: Optional chapter filter

        Returns:
            List of attempt summaries
        """
        query = select(QuizAttempt).where(QuizAttempt.user_id == user_id)

        if chapter_id:
            # Filter by chapter - need to join with Quiz
            quiz_summary = await self.get_quiz_for_chapter(chapter_id)
            if quiz_summary:
                query = query.where(QuizAttempt.quiz_id == quiz_summary.id)

        query = query.order_by(QuizAttempt.started_at.desc())

        result = await self.db.execute(query)
        attempts = result.scalars().all()

        return [
            {
                "id": a.id,
                "quiz_id": a.quiz_id,
                "started_at": a.started_at.isoformat() if a.started_at else None,
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
                "score": a.score,
                "passed": a.passed,
                "time_taken_seconds": a.time_taken_seconds,
            }
            for a in attempts
        ]
