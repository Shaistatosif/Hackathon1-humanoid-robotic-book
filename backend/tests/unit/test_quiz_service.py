"""Unit tests for QuizService and data classes."""

import pytest

from src.services.quiz_service import (
    AnswerResult,
    QuestionData,
    QuizResult,
    QuizSummary,
)


class TestQuizSummary:
    """Tests for QuizSummary dataclass."""

    def test_quiz_summary_creation(self):
        """Test creating a QuizSummary."""
        summary = QuizSummary(
            id="quiz-1",
            chapter_id="chapter-1",
            title="Test Quiz",
            description="A test quiz",
            question_count=5,
            passing_score=70,
            time_limit_minutes=30,
        )

        assert summary.id == "quiz-1"
        assert summary.chapter_id == "chapter-1"
        assert summary.title == "Test Quiz"
        assert summary.description == "A test quiz"
        assert summary.question_count == 5
        assert summary.passing_score == 70
        assert summary.time_limit_minutes == 30

    def test_quiz_summary_to_dict(self):
        """Test QuizSummary.to_dict() method."""
        summary = QuizSummary(
            id="quiz-1",
            chapter_id="chapter-1",
            title="Test Quiz",
            description="A test quiz",
            question_count=5,
            passing_score=70,
            time_limit_minutes=30,
        )

        result = summary.to_dict()

        assert result == {
            "id": "quiz-1",
            "chapter_id": "chapter-1",
            "title": "Test Quiz",
            "description": "A test quiz",
            "question_count": 5,
            "passing_score": 70,
            "time_limit_minutes": 30,
        }

    def test_quiz_summary_none_values(self):
        """Test QuizSummary with None values."""
        summary = QuizSummary(
            id="quiz-1",
            chapter_id="chapter-1",
            title="Test Quiz",
            description=None,
            question_count=5,
            passing_score=70,
            time_limit_minutes=None,
        )

        result = summary.to_dict()
        assert result["description"] is None
        assert result["time_limit_minutes"] is None


class TestQuestionData:
    """Tests for QuestionData dataclass."""

    def test_question_data_multiple_choice(self):
        """Test creating multiple choice QuestionData."""
        question = QuestionData(
            id="q-1",
            question_type="multiple_choice",
            question_text="What is 2 + 2?",
            options=["3", "4", "5", "6"],
            points=10,
            order=1,
        )

        assert question.id == "q-1"
        assert question.question_type == "multiple_choice"
        assert question.options == ["3", "4", "5", "6"]
        assert question.points == 10

    def test_question_data_true_false(self):
        """Test creating true/false QuestionData."""
        question = QuestionData(
            id="q-2",
            question_type="true_false",
            question_text="The sky is blue.",
            options=None,
            points=5,
            order=2,
        )

        assert question.question_type == "true_false"
        assert question.options is None

    def test_question_data_to_dict(self):
        """Test QuestionData.to_dict() method."""
        question = QuestionData(
            id="q-1",
            question_type="multiple_choice",
            question_text="What is 2 + 2?",
            options=["3", "4", "5", "6"],
            points=10,
            order=1,
        )

        result = question.to_dict()

        assert result == {
            "id": "q-1",
            "question_type": "multiple_choice",
            "question_text": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "points": 10,
            "order": 1,
        }


class TestAnswerResult:
    """Tests for AnswerResult dataclass."""

    def test_answer_result_correct(self):
        """Test creating a correct AnswerResult."""
        answer = AnswerResult(
            question_id="q-1",
            question_text="What is 2 + 2?",
            user_answer="4",
            correct_answer="4",
            is_correct=True,
            explanation="Basic addition",
            points_earned=10,
            points_possible=10,
        )

        assert answer.is_correct is True
        assert answer.points_earned == answer.points_possible

    def test_answer_result_incorrect(self):
        """Test creating an incorrect AnswerResult."""
        answer = AnswerResult(
            question_id="q-1",
            question_text="What is 2 + 2?",
            user_answer="5",
            correct_answer="4",
            is_correct=False,
            explanation="Basic addition",
            points_earned=0,
            points_possible=10,
        )

        assert answer.is_correct is False
        assert answer.points_earned == 0

    def test_answer_result_to_dict(self):
        """Test AnswerResult.to_dict() method."""
        answer = AnswerResult(
            question_id="q-1",
            question_text="What is 2 + 2?",
            user_answer="4",
            correct_answer="4",
            is_correct=True,
            explanation="Basic addition",
            points_earned=10,
            points_possible=10,
        )

        result = answer.to_dict()

        assert result == {
            "question_id": "q-1",
            "question_text": "What is 2 + 2?",
            "user_answer": "4",
            "correct_answer": "4",
            "is_correct": True,
            "explanation": "Basic addition",
            "points_earned": 10,
            "points_possible": 10,
        }


class TestQuizResult:
    """Tests for QuizResult dataclass."""

    def test_quiz_result_passed(self):
        """Test creating a passing QuizResult."""
        answers = [
            AnswerResult(
                question_id="q-1",
                question_text="Question 1",
                user_answer="A",
                correct_answer="A",
                is_correct=True,
                explanation=None,
                points_earned=10,
                points_possible=10,
            ),
            AnswerResult(
                question_id="q-2",
                question_text="Question 2",
                user_answer="B",
                correct_answer="B",
                is_correct=True,
                explanation=None,
                points_earned=10,
                points_possible=10,
            ),
        ]

        result = QuizResult(
            attempt_id="attempt-1",
            quiz_id="quiz-1",
            score=100.0,
            passed=True,
            total_points=20,
            earned_points=20,
            time_taken_seconds=120,
            answers=answers,
        )

        assert result.passed is True
        assert result.score == 100.0
        assert result.earned_points == result.total_points
        assert len(result.answers) == 2

    def test_quiz_result_failed(self):
        """Test creating a failing QuizResult."""
        answers = [
            AnswerResult(
                question_id="q-1",
                question_text="Question 1",
                user_answer="A",
                correct_answer="B",
                is_correct=False,
                explanation=None,
                points_earned=0,
                points_possible=10,
            ),
        ]

        result = QuizResult(
            attempt_id="attempt-1",
            quiz_id="quiz-1",
            score=0.0,
            passed=False,
            total_points=10,
            earned_points=0,
            time_taken_seconds=60,
            answers=answers,
        )

        assert result.passed is False
        assert result.score == 0.0

    def test_quiz_result_to_dict(self):
        """Test QuizResult.to_dict() method."""
        answers = [
            AnswerResult(
                question_id="q-1",
                question_text="Question 1",
                user_answer="A",
                correct_answer="A",
                is_correct=True,
                explanation="Correct!",
                points_earned=10,
                points_possible=10,
            ),
        ]

        result = QuizResult(
            attempt_id="attempt-1",
            quiz_id="quiz-1",
            score=100.0,
            passed=True,
            total_points=10,
            earned_points=10,
            time_taken_seconds=60,
            answers=answers,
        )

        result_dict = result.to_dict()

        assert result_dict["attempt_id"] == "attempt-1"
        assert result_dict["quiz_id"] == "quiz-1"
        assert result_dict["score"] == 100.0
        assert result_dict["passed"] is True
        assert result_dict["total_points"] == 10
        assert result_dict["earned_points"] == 10
        assert result_dict["time_taken_seconds"] == 60
        assert len(result_dict["answers"]) == 1
        assert result_dict["answers"][0]["is_correct"] is True

    def test_quiz_result_no_time_limit(self):
        """Test QuizResult without time tracking."""
        result = QuizResult(
            attempt_id="attempt-1",
            quiz_id="quiz-1",
            score=80.0,
            passed=True,
            total_points=10,
            earned_points=8,
            time_taken_seconds=None,
            answers=[],
        )

        result_dict = result.to_dict()
        assert result_dict["time_taken_seconds"] is None
