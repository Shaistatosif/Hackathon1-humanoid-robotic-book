/**
 * ProgressCard component showing chapter completion status.
 *
 * Displays overall reading progress with visual indicators.
 */

import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

interface ChapterProgress {
  chapter_id: string;
  status: string;
  progress_percent: number;
  time_spent_seconds: number;
}

interface ProgressCardProps {
  progress: ChapterProgress[];
  totalChapters?: number;
}

const chapterTitles: Record<string, string> = {
  'chapter-1': 'Introduction to Humanoid Robotics',
  'chapter-2': 'Robot Components and Architecture',
  'chapter-3': 'Sensors and Actuators',
};

function formatTime(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const remainingMins = minutes % 60;
  return `${hours}h ${remainingMins}m`;
}

export default function ProgressCard({
  progress,
  totalChapters = 3,
}: ProgressCardProps): JSX.Element {
  const completedCount = progress.filter((p) => p.status === 'completed').length;
  const overallPercent = totalChapters > 0
    ? Math.round((completedCount / totalChapters) * 100)
    : 0;

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h3 className={styles.cardTitle}>Reading Progress</h3>
        <span className={styles.overallProgress}>{overallPercent}% Complete</span>
      </div>

      <div className={styles.progressBar}>
        <div
          className={styles.progressFill}
          style={{ width: `${overallPercent}%` }}
        />
      </div>

      <div className={styles.chapterList}>
        {['chapter-1', 'chapter-2', 'chapter-3'].map((chapterId) => {
          const chapterProgress = progress.find((p) => p.chapter_id === chapterId);
          const percent = chapterProgress?.progress_percent || 0;
          const status = chapterProgress?.status || 'not_started';
          const timeSpent = chapterProgress?.time_spent_seconds || 0;

          return (
            <div key={chapterId} className={styles.chapterItem}>
              <div className={styles.chapterInfo}>
                <Link to={`/${chapterId}`} className={styles.chapterLink}>
                  {chapterTitles[chapterId] || chapterId}
                </Link>
                <div className={styles.chapterMeta}>
                  <span className={`${styles.statusBadge} ${styles[status]}`}>
                    {status === 'completed' ? 'Completed' :
                     status === 'in_progress' ? 'In Progress' : 'Not Started'}
                  </span>
                  {timeSpent > 0 && (
                    <span className={styles.timeSpent}>{formatTime(timeSpent)}</span>
                  )}
                </div>
              </div>
              <div className={styles.chapterProgressBar}>
                <div
                  className={styles.chapterProgressFill}
                  style={{ width: `${percent}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
