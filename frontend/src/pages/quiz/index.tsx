/**
 * Quiz index page listing all available chapter quizzes.
 */

import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

interface QuizInfo {
  chapterId: string;
  title: string;
  description: string;
  questionCount: number;
}

const availableQuizzes: QuizInfo[] = [
  {
    chapterId: 'chapter-1',
    title: 'Introduction to Humanoid Robotics',
    description: 'Test your understanding of humanoid robot fundamentals, history, and applications.',
    questionCount: 5,
  },
  {
    chapterId: 'chapter-2',
    title: 'Robot Components and Architecture',
    description: 'Test your knowledge of humanoid robot hardware, software architecture, and power systems.',
    questionCount: 5,
  },
  {
    chapterId: 'chapter-3',
    title: 'Sensors and Actuators',
    description: 'Test your understanding of robot sensing systems, sensor fusion, and actuator control.',
    questionCount: 5,
  },
];

export default function QuizIndexPage(): JSX.Element {
  return (
    <Layout
      title="Chapter Quizzes"
      description="Test your knowledge with interactive chapter quizzes"
    >
      <div className={styles.quizListPage}>
        <div className={styles.container}>
          <div className={styles.pageHeader}>
            <h1>Chapter Quizzes</h1>
            <p>
              Test your understanding of humanoid robotics concepts with interactive quizzes.
              Complete each quiz after studying the corresponding chapter.
            </p>
          </div>

          <div className={styles.quizGrid}>
            {availableQuizzes.map((quiz) => (
              <div key={quiz.chapterId} className={styles.quizCard}>
                <h3>{quiz.title}</h3>
                <p>{quiz.description}</p>
                <div className={styles.quizMeta}>
                  <span>{quiz.questionCount} Questions</span>
                  <span>Passing: 70%</span>
                </div>
                <Link
                  to={`/quiz/${quiz.chapterId}`}
                  className={styles.startQuizButton}
                >
                  Start Quiz →
                </Link>
              </div>
            ))}
          </div>

          <div className={styles.backSection}>
            <Link to="/" className={styles.backLink}>
              ← Back to Textbook
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
}
