/**
 * Quiz page for chapter assessments.
 *
 * Dynamic route that loads quizzes based on chapter ID.
 */

import React from 'react';
import { useLocation } from '@docusaurus/router';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import Quiz from '../../components/Quiz';
import styles from './styles.module.css';

// Chapter titles for display
const chapterTitles: Record<string, string> = {
  'chapter-1': 'Introduction to Humanoid Robotics',
  'chapter-2': 'Robot Components and Architecture',
  'chapter-3': 'Sensors and Actuators',
};

export default function QuizPage(): JSX.Element {
  const location = useLocation();

  // Extract chapter ID from URL path
  const pathParts = location.pathname.split('/');
  const chapterId = pathParts[pathParts.length - 1] || pathParts[pathParts.length - 2];

  const chapterTitle = chapterTitles[chapterId] || chapterId;
  const isValidChapter = chapterId in chapterTitles;

  if (!isValidChapter) {
    return (
      <Layout title="Quiz Not Found">
        <div className={styles.quizPage}>
          <div className={styles.container}>
            <h1>Quiz Not Found</h1>
            <p>The requested quiz could not be found.</p>
            <Link to="/" className={styles.backLink}>
              Return to Textbook
            </Link>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout
      title={`Quiz: ${chapterTitle}`}
      description={`Test your knowledge of ${chapterTitle}`}
    >
      <div className={styles.quizPage}>
        <div className={styles.container}>
          <div className={styles.breadcrumb}>
            <Link to="/">Home</Link>
            <span className={styles.separator}>/</span>
            <Link to={`/${chapterId}`}>{chapterTitle}</Link>
            <span className={styles.separator}>/</span>
            <span>Quiz</span>
          </div>

          <Quiz
            chapterId={chapterId}
            onComplete={(result) => {
              console.log('Quiz completed:', result);
            }}
          />

          <div className={styles.backSection}>
            <Link to={`/${chapterId}`} className={styles.backLink}>
              ← Back to Chapter
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
}
