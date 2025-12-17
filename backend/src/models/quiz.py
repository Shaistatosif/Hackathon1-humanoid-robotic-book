"""Quiz models for chapter assessments.

Provides models for quizzes, questions, and user attempts.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class QuestionType(str, PyEnum):
    """Types of quiz questions."""

    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"


class Quiz(Base):
    """Quiz for a chapter.

    Attributes:
        id: Unique quiz identifier.
        chapter_id: Associated chapter ID.
        title: Quiz title.
        description: Optional quiz description.
        passing_score: Minimum score to pass (0-100).
        time_limit_minutes: Optional time limit.
        is_active: Whether quiz is available.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    chapter_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    passing_score: Mapped[int] = mapped_column(
        Integer,
        default=70,
        nullable=False,
    )
    time_limit_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="Question.order",
    )
    attempts: Mapped[list["QuizAttempt"]] = relationship(
        "QuizAttempt",
        back_populates="quiz",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of Quiz."""
        return f"<Quiz {self.id}: {self.title}>"

    @property
    def question_count(self) -> int:
        """Get total number of questions."""
        return len(self.questions) if self.questions else 0


class Question(Base):
    """Quiz question.

    Attributes:
        id: Unique question identifier.
        quiz_id: Parent quiz ID.
        question_type: Type of question (MCQ, short answer, etc.).
        question_text: The question content.
        options_json: JSON array of options for MCQ.
        correct_answer: The correct answer.
        explanation: Explanation of the correct answer.
        points: Points awarded for correct answer.
        order: Display order within quiz.
    """

    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    quiz_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_type: Mapped[str] = mapped_column(
        Enum(QuestionType),
        default=QuestionType.MULTIPLE_CHOICE,
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    options_json: Mapped[str | None] = mapped_column(
        Text,  # JSON array: ["Option A", "Option B", "Option C", "Option D"]
        nullable=True,
    )
    correct_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    points: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    quiz: Mapped["Quiz"] = relationship(
        "Quiz",
        back_populates="questions",
    )

    def __repr__(self) -> str:
        """String representation of Question."""
        return f"<Question {self.id}: {self.question_text[:50]}...>"

    @property
    def options(self) -> list[str] | None:
        """Parse options from JSON string."""
        if not self.options_json:
            return None
        import json
        try:
            return json.loads(self.options_json)
        except json.JSONDecodeError:
            return None

    @options.setter
    def options(self, value: list[str] | None) -> None:
        """Set options as JSON string."""
        if value is None:
            self.options_json = None
        else:
            import json
            self.options_json = json.dumps(value)


class QuizAttempt(Base):
    """User's attempt at a quiz.

    Attributes:
        id: Unique attempt identifier.
        quiz_id: Quiz being attempted.
        user_id: User making the attempt.
        started_at: When attempt started.
        completed_at: When attempt was submitted.
        score: Achieved score (0-100).
        passed: Whether passing score was achieved.
        answers_json: JSON object of user answers.
        time_taken_seconds: Time taken to complete.
    """

    __tablename__ = "quiz_attempts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    quiz_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    passed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )
    answers_json: Mapped[str | None] = mapped_column(
        Text,  # JSON object: {"question_id": "user_answer", ...}
        nullable=True,
    )
    time_taken_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Relationships
    quiz: Mapped["Quiz"] = relationship(
        "Quiz",
        back_populates="attempts",
    )

    def __repr__(self) -> str:
        """String representation of QuizAttempt."""
        status = "completed" if self.completed_at else "in_progress"
        return f"<QuizAttempt {self.id} ({status})>"

    @property
    def answers(self) -> dict[str, str] | None:
        """Parse answers from JSON string."""
        if not self.answers_json:
            return None
        import json
        try:
            return json.loads(self.answers_json)
        except json.JSONDecodeError:
            return None

    @answers.setter
    def answers(self, value: dict[str, str] | None) -> None:
        """Set answers as JSON string."""
        if value is None:
            self.answers_json = None
        else:
            import json
            self.answers_json = json.dumps(value)

    @property
    def is_complete(self) -> bool:
        """Check if attempt is completed."""
        return self.completed_at is not None
