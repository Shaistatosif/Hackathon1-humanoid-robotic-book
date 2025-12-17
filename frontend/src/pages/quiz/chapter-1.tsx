/**
 * Quiz page for Chapter 1: Introduction to Humanoid Robotics.
 */

import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import Quiz from '../../components/Quiz';
import styles from './styles.module.css';

const CHAPTER_ID = 'chapter-1';
const CHAPTER_TITLE = 'Introduction to Humanoid Robotics';

export default function Chapter1QuizPage(): JSX.Element {
  return (
    <Layout
      title={`Quiz: ${CHAPTER_TITLE}`}
      description={`Test your knowledge of ${CHAPTER_TITLE}`}
    >
      <div className={styles.quizPage}>
        <div className={styles.container}>
          <div className={styles.breadcrumb}>
            <Link to="/">Home</Link>
            <span className={styles.separator}>/</span>
            <Link to={`/${CHAPTER_ID}`}>{CHAPTER_TITLE}</Link>
            <span className={styles.separator}>/</span>
            <span>Quiz</span>
          </div>

          <Quiz
            chapterId={CHAPTER_ID}
            onComplete={(_result) => {
              // Quiz completion handled by component
            }}
          />

          <div className={styles.backSection}>
            <Link to={`/${CHAPTER_ID}`} className={styles.backLink}>
              ← Back to Chapter
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
}
