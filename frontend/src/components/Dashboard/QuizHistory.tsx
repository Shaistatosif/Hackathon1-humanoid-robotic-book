/**
 * QuizHistory component showing past quiz attempts and scores.
 *
 * Displays quiz history with scores and retry options.
 */

import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

interface QuizAttempt {
  id: string;
  quiz_id: string;
  score: number;
  total_questions: number;
  correct_answers: number;
  completed_at: string | null;
}

interface QuizHistoryProps {
  attempts: QuizAttempt[];
}

const quizTitles: Record<string, string> = {
  'chapter-1-quiz': 'Introduction to Humanoid Robotics',
  'chapter-2-quiz': 'Robot Components and Architecture',
  'chapter-3-quiz': 'Sensors and Actuators',
};

function formatDate(isoDate: string): string {
  const date = new Date(isoDate);
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getScoreClass(score: number): string {
  if (score >= 80) return styles.scoreHigh;
  if (score >= 60) return styles.scoreMedium;
  return styles.scoreLow;
}

export default function QuizHistory({ attempts }: QuizHistoryProps): JSX.Element {
  if (attempts.length === 0) {
    return (
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h3 className={styles.cardTitle}>Quiz History</h3>
        </div>
        <div className={styles.emptyState}>
          <span className={styles.emptyIcon}>📝</span>
          <p>No quizzes taken yet</p>
          <span className={styles.emptyHint}>
            Complete chapters and test your knowledge
          </span>
        </div>
      </div>
    );
  }

  // Calculate average score
  const avgScore = attempts.reduce((sum, a) => sum + a.score, 0) / attempts.length;

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h3 className={styles.cardTitle}>Quiz History</h3>
        <span className={styles.avgScore}>
          Avg: {avgScore.toFixed(0)}%
        </span>
      </div>

      <ul className={styles.quizList}>
        {attempts.map((attempt) => {
          const chapterId = attempt.quiz_id?.replace('-quiz', '') || '';
          const title = quizTitles[attempt.quiz_id] || attempt.quiz_id;

          return (
            <li key={attempt.id} className={styles.quizItem}>
              <div className={styles.quizInfo}>
                <span className={styles.quizTitle}>{title}</span>
                <span className={styles.quizMeta}>
                  {attempt.correct_answers}/{attempt.total_questions} correct
                  {attempt.completed_at && (
                    <> • {formatDate(attempt.completed_at)}</>
                  )}
                </span>
              </div>
              <div className={styles.quizActions}>
                <span className={`${styles.quizScore} ${getScoreClass(attempt.score)}`}>
                  {attempt.score.toFixed(0)}%
                </span>
                <Link
                  to={`/quiz/${chapterId}`}
                  className={styles.retryButton}
                >
                  Retry
                </Link>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
