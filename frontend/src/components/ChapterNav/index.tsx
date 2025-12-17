/**
 * Chapter Navigation Component
 *
 * Provides previous/next chapter navigation, quiz access, and quick links.
 */

import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

interface ChapterInfo {
  title: string;
  slug: string;
}

interface ChapterNavProps {
  previous?: ChapterInfo;
  next?: ChapterInfo;
  currentChapter?: string;
  chapterId?: string;
  showQuizButton?: boolean;
}

export default function ChapterNav({
  previous,
  next,
  currentChapter,
  chapterId,
  showQuizButton = true,
}: ChapterNavProps): JSX.Element {
  // Determine if this is a chapter page that should have a quiz
  const hasQuiz = chapterId && chapterId.startsWith('chapter-');

  return (
    <nav className={styles.chapterNav} aria-label="Chapter navigation">
      {/* Quiz Button */}
      {showQuizButton && hasQuiz && (
        <div className={styles.quizSection}>
          <Link to={`/quiz/${chapterId}`} className={styles.quizButton}>
            <span className={styles.quizIcon}>📝</span>
            <span className={styles.quizText}>Take Chapter Quiz</span>
          </Link>
        </div>
      )}

      <div className={styles.navContainer}>
        {previous ? (
          <Link to={previous.slug} className={styles.navLink}>
            <span className={styles.navDirection}>Previous Chapter</span>
            <span className={styles.navTitle}>{previous.title}</span>
          </Link>
        ) : (
          <div className={styles.navPlaceholder} />
        )}

        {currentChapter && (
          <div className={styles.currentChapter}>
            <span className={styles.currentLabel}>Current</span>
            <span className={styles.currentTitle}>{currentChapter}</span>
          </div>
        )}

        {next ? (
          <Link to={next.slug} className={`${styles.navLink} ${styles.navNext}`}>
            <span className={styles.navDirection}>Next Chapter</span>
            <span className={styles.navTitle}>{next.title}</span>
          </Link>
        ) : (
          <div className={styles.navPlaceholder} />
        )}
      </div>
    </nav>
  );
}

/**
 * Predefined chapter structure for the textbook.
 */
export const chapters: ChapterInfo[] = [
  { title: 'Introduction', slug: '/' },
  { title: 'Chapter 1: Introduction to Humanoid Robotics', slug: '/chapter-1' },
  { title: 'Chapter 2: Robot Components', slug: '/chapter-2' },
  { title: 'Chapter 3: Sensors and Actuators', slug: '/chapter-3' },
];

/**
 * Get navigation info for a chapter by its slug.
 */
export function getChapterNavInfo(currentSlug: string): {
  previous?: ChapterInfo;
  next?: ChapterInfo;
  current?: ChapterInfo;
} {
  const currentIndex = chapters.findIndex((c) => c.slug === currentSlug);

  if (currentIndex === -1) {
    return {};
  }

  return {
    previous: currentIndex > 0 ? chapters[currentIndex - 1] : undefined,
    next: currentIndex < chapters.length - 1 ? chapters[currentIndex + 1] : undefined,
    current: chapters[currentIndex],
  };
}
