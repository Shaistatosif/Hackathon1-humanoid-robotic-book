/**
 * Recommendations component showing personalized learning suggestions.
 *
 * Displays AI-generated recommendations based on user progress.
 */

import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

interface Recommendation {
  type: string;
  chapter_id: string;
  title: string;
  description: string;
  priority: number;
}

interface RecommendationsProps {
  recommendations: Recommendation[];
}

const chapterTitles: Record<string, string> = {
  'chapter-1': 'Introduction to Humanoid Robotics',
  'chapter-2': 'Robot Components and Architecture',
  'chapter-3': 'Sensors and Actuators',
};

function getRecommendationIcon(type: string): string {
  switch (type) {
    case 'continue':
      return '📖';
    case 'start':
      return '🚀';
    case 'quiz':
      return '📝';
    case 'retry_quiz':
      return '🔄';
    default:
      return '💡';
  }
}

function getRecommendationLink(rec: Recommendation): string {
  switch (rec.type) {
    case 'quiz':
    case 'retry_quiz':
      return `/quiz/${rec.chapter_id}`;
    default:
      return `/${rec.chapter_id}`;
  }
}

function getActionLabel(type: string): string {
  switch (type) {
    case 'continue':
      return 'Continue';
    case 'start':
      return 'Start';
    case 'quiz':
      return 'Take Quiz';
    case 'retry_quiz':
      return 'Retry Quiz';
    default:
      return 'Go';
  }
}

export default function Recommendations({
  recommendations,
}: RecommendationsProps): JSX.Element {
  if (recommendations.length === 0) {
    return (
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h3 className={styles.cardTitle}>Recommendations</h3>
        </div>
        <div className={styles.emptyState}>
          <span className={styles.emptyIcon}>🎉</span>
          <p>Great job!</p>
          <span className={styles.emptyHint}>
            You&apos;re all caught up. Keep exploring!
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h3 className={styles.cardTitle}>Recommended Next Steps</h3>
      </div>

      <ul className={styles.recommendationList}>
        {recommendations.map((rec, index) => (
          <li key={index} className={styles.recommendationItem}>
            <span className={styles.recommendationIcon}>
              {getRecommendationIcon(rec.type)}
            </span>
            <div className={styles.recommendationContent}>
              <span className={styles.recommendationChapter}>
                {chapterTitles[rec.chapter_id] || rec.chapter_id}
              </span>
              <span className={styles.recommendationDesc}>
                {rec.description}
              </span>
            </div>
            <Link
              to={getRecommendationLink(rec)}
              className={styles.recommendationAction}
            >
              {getActionLabel(rec.type)}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
