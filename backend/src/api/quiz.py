"""Quiz API router.

Provides endpoints for quiz access, attempts, and scoring.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user_optional
from src.models.user import User
from src.services.quiz_service import QuizService

router = APIRouter(prefix="/quiz", tags=["Quizzes"])


# Request/Response schemas
class QuizSummaryResponse(BaseModel):
    """Quiz summary response."""

    id: str
    chapter_id: str
    title: str
    description: str | None
    question_count: int
    passing_score: int
    time_limit_minutes: int | None


class QuestionResponse(BaseModel):
    """Question for display (without correct answer)."""

    id: str
    question_type: str
    question_text: str
    options: list[str] | None
    points: int
    order: int


class QuizQuestionsResponse(BaseModel):
    """Quiz questions response."""

    quiz_id: str
    chapter_id: str
    title: str
    questions: list[QuestionResponse]
    time_limit_minutes: int | None


class StartAttemptRequest(BaseModel):
    """Start quiz attempt request."""

    chapter_id: str = Field(..., description="Chapter ID for quiz")


class StartAttemptResponse(BaseModel):
    """Start attempt response."""

    attempt_id: str
    quiz_id: str
    started_at: str


class SubmitAnswersRequest(BaseModel):
    """Submit quiz answers request."""

    attempt_id: str = Field(..., description="Quiz attempt ID")
    answers: dict[str, str] = Field(..., description="Question ID to answer mapping")


class AnswerResultResponse(BaseModel):
    """Result for a single answer."""

    question_id: str
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str | None
    points_earned: int
    points_possible: int


class QuizResultResponse(BaseModel):
    """Complete quiz result response."""

    attempt_id: str
    quiz_id: str
    score: float
    passed: bool
    total_points: int
    earned_points: int
    time_taken_seconds: int | None
    answers: list[AnswerResultResponse]


class AttemptSummaryResponse(BaseModel):
    """Summary of a quiz attempt."""

    id: str
    quiz_id: str
    started_at: str | None
    completed_at: str | None
    score: float | None
    passed: bool | None
    time_taken_seconds: int | None


@router.get("/chapter/{chapter_id}", response_model=QuizSummaryResponse)
async def get_quiz_for_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get quiz summary for a chapter.

    Returns quiz metadata without questions.
    """
    service = QuizService(db)
    quiz = await service.get_quiz_for_chapter(chapter_id)

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quiz found for chapter: {chapter_id}",
        )

    return QuizSummaryResponse(**quiz.to_dict())


@router.get("/chapter/{chapter_id}/questions", response_model=QuizQuestionsResponse)
async def get_quiz_questions(
    chapter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get quiz questions for a chapter.

    Returns questions without correct answers for taking the quiz.
    """
    service = QuizService(db)
    quiz = await service.get_quiz_for_chapter(chapter_id)

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quiz found for chapter: {chapter_id}",
        )

    questions = await service.get_quiz_questions(chapter_id)

    return QuizQuestionsResponse(
        quiz_id=quiz.id,
        chapter_id=chapter_id,
        title=quiz.title,
        questions=[QuestionResponse(**q.to_dict()) for q in questions],
        time_limit_minutes=quiz.time_limit_minutes,
    )


@router.post("/start", response_model=StartAttemptResponse)
async def start_quiz_attempt(
    request: StartAttemptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Start a new quiz attempt.

    Creates a new attempt record and returns the attempt ID.
    """
    service = QuizService(db)

    try:
        attempt = await service.start_attempt(
            chapter_id=request.chapter_id,
            user_id=current_user.id if current_user else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return StartAttemptResponse(
        attempt_id=attempt.id,
        quiz_id=attempt.quiz_id,
        started_at=attempt.started_at.isoformat(),
    )


@router.post("/submit", response_model=QuizResultResponse)
async def submit_quiz_answers(
    request: SubmitAnswersRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit quiz answers and get results.

    Scores the answers and returns detailed results.
    """
    service = QuizService(db)

    try:
        result = await service.submit_answers(
            attempt_id=request.attempt_id,
            answers=request.answers,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return QuizResultResponse(
        attempt_id=result.attempt_id,
        quiz_id=result.quiz_id,
        score=result.score,
        passed=result.passed,
        total_points=result.total_points,
        earned_points=result.earned_points,
        time_taken_seconds=result.time_taken_seconds,
        answers=[
            AnswerResultResponse(**a.to_dict())
            for a in result.answers
        ],
    )


@router.get("/attempt/{attempt_id}", response_model=QuizResultResponse)
async def get_attempt_result(
    attempt_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get result for a completed quiz attempt."""
    service = QuizService(db)
    result = await service.get_attempt_result(attempt_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found or not completed",
        )

    return QuizResultResponse(
        attempt_id=result.attempt_id,
        quiz_id=result.quiz_id,
        score=result.score,
        passed=result.passed,
        total_points=result.total_points,
        earned_points=result.earned_points,
        time_taken_seconds=result.time_taken_seconds,
        answers=[
            AnswerResultResponse(**a.to_dict())
            for a in result.answers
        ],
    )


@router.get("/history", response_model=list[AttemptSummaryResponse])
async def get_user_quiz_history(
    chapter_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Get quiz attempt history for current user.

    Optionally filter by chapter ID.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view quiz history",
        )

    service = QuizService(db)
    attempts = await service.get_user_attempts(
        user_id=current_user.id,
        chapter_id=chapter_id,
    )

    return [AttemptSummaryResponse(**a) for a in attempts]


@router.get("/chapters", response_model=list[QuizSummaryResponse])
async def list_available_quizzes(
    db: AsyncSession = Depends(get_db),
):
    """List all available quizzes.

    Returns summaries of quizzes for all chapters.
    """
    service = QuizService(db)

    # Check known chapters
    chapters = ["chapter-1", "chapter-2", "chapter-3"]
    quizzes = []

    for chapter_id in chapters:
        quiz = await service.get_quiz_for_chapter(chapter_id)
        if quiz:
            quizzes.append(QuizSummaryResponse(**quiz.to_dict()))

    return quizzes
