/**
 * QuizResults component for displaying quiz results and answer review.
 */

import React, { useState } from 'react';
import styles from './styles.module.css';

interface AnswerResult {
  question_id: string;
  question_text: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string | null;
  points_earned: number;
  points_possible: number;
}

interface QuizResult {
  attempt_id: string;
  quiz_id: string;
  score: number;
  passed: boolean;
  total_points: number;
  earned_points: number;
  time_taken_seconds: number | null;
  answers: AnswerResult[];
}

interface QuizResultsProps {
  result: QuizResult;
  onRetry?: () => void;
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

export default function QuizResults({
  result,
  onRetry,
}: QuizResultsProps): JSX.Element {
  const [showDetails, setShowDetails] = useState(false);

  const { score, passed, earned_points, total_points, time_taken_seconds, answers } = result;
  const correctCount = answers.filter((a) => a.is_correct).length;

  return (
    <div className={styles.results}>
      {/* Score Summary */}
      <div className={`${styles.scoreSummary} ${passed ? styles.passed : styles.failed}`}>
        <div className={styles.scoreCircle}>
          <span className={styles.scoreValue}>{Math.round(score)}%</span>
        </div>
        <h2 className={styles.resultTitle}>
          {passed ? 'Congratulations!' : 'Keep Learning!'}
        </h2>
        <p className={styles.resultMessage}>
          {passed
            ? 'You passed the quiz!'
            : 'You need 70% to pass. Review the material and try again.'}
        </p>
      </div>

      {/* Stats */}
      <div className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Correct Answers</span>
          <span className={styles.statValue}>{correctCount} / {answers.length}</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Points Earned</span>
          <span className={styles.statValue}>{earned_points} / {total_points}</span>
        </div>
        {time_taken_seconds !== null && (
          <div className={styles.stat}>
            <span className={styles.statLabel}>Time Taken</span>
            <span className={styles.statValue}>{formatTime(time_taken_seconds)}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className={styles.actions}>
        <button
          className={styles.detailsButton}
          onClick={() => setShowDetails(!showDetails)}
        >
          {showDetails ? 'Hide Details' : 'Review Answers'}
        </button>
        {onRetry && (
          <button className={styles.retryButton} onClick={onRetry}>
            Try Again
          </button>
        )}
      </div>

      {/* Answer Details */}
      {showDetails && (
        <div className={styles.answerReview}>
          <h3>Answer Review</h3>
          {answers.map((answer, index) => (
            <div
              key={answer.question_id}
              className={`${styles.answerItem} ${
                answer.is_correct ? styles.correct : styles.incorrect
              }`}
            >
              <div className={styles.answerHeader}>
                <span className={styles.answerNumber}>Q{index + 1}</span>
                <span className={styles.answerStatus}>
                  {answer.is_correct ? '✓ Correct' : '✗ Incorrect'}
                </span>
              </div>
              <p className={styles.answerQuestion}>{answer.question_text}</p>
              <div className={styles.answerDetails}>
                <div className={styles.answerRow}>
                  <span className={styles.answerLabel}>Your Answer:</span>
                  <span className={answer.is_correct ? styles.correctText : styles.incorrectText}>
                    {answer.user_answer || '(No answer)'}
                  </span>
                </div>
                {!answer.is_correct && (
                  <div className={styles.answerRow}>
                    <span className={styles.answerLabel}>Correct Answer:</span>
                    <span className={styles.correctText}>{answer.correct_answer}</span>
                  </div>
                )}
                {answer.explanation && (
                  <div className={styles.explanation}>
                    <strong>Explanation:</strong> {answer.explanation}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
