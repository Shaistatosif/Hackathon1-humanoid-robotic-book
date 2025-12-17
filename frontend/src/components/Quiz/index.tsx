/**
 * Quiz component for chapter assessments.
 *
 * Displays quiz questions and handles answer submission.
 */

import React, { useState, useEffect } from 'react';
import { get, post } from '../../services/api';
import QuizQuestion from './QuizQuestion';
import QuizResults from './QuizResults';
import styles from './styles.module.css';

interface Question {
  id: string;
  question_type: string;
  question_text: string;
  options: string[] | null;
  points: number;
  order: number;
}

interface QuizData {
  quiz_id: string;
  chapter_id: string;
  title: string;
  questions: Question[];
  time_limit_minutes: number | null;
}

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

interface QuizProps {
  chapterId: string;
  onComplete?: (result: QuizResult) => void;
}

type QuizState = 'loading' | 'ready' | 'taking' | 'submitting' | 'results' | 'error';

export default function Quiz({ chapterId, onComplete }: QuizProps): JSX.Element {
  const [state, setState] = useState<QuizState>('loading');
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<Date | null>(null);

  // Load quiz data
  useEffect(() => {
    loadQuiz();
  }, [chapterId]);

  async function loadQuiz() {
    setState('loading');
    setError(null);

    try {
      const data = await get<QuizData>(`/api/quiz/chapter/${chapterId}/questions`);
      setQuizData(data);
      setState('ready');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load quiz');
      setState('error');
    }
  }

  async function startQuiz() {
    setState('loading');

    try {
      const response = await post<{ attempt_id: string }>('/api/quiz/start', {
        chapter_id: chapterId,
      });
      setAttemptId(response.attempt_id);
      setAnswers({});
      setStartTime(new Date());
      setState('taking');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start quiz');
      setState('error');
    }
  }

  function handleAnswerChange(questionId: string, answer: string) {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  }

  async function submitQuiz() {
    if (!attemptId) return;

    setState('submitting');

    try {
      const quizResult = await post<QuizResult>('/api/quiz/submit', {
        attempt_id: attemptId,
        answers,
      });
      setResult(quizResult);
      setState('results');
      onComplete?.(quizResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit quiz');
      setState('error');
    }
  }

  function retryQuiz() {
    setResult(null);
    setAttemptId(null);
    setAnswers({});
    setState('ready');
  }

  // Calculate progress
  const answeredCount = Object.keys(answers).length;
  const totalQuestions = quizData?.questions.length || 0;
  const allAnswered = answeredCount === totalQuestions && totalQuestions > 0;

  // Render loading state
  if (state === 'loading') {
    return (
      <div className={styles.quizContainer}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading quiz...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (state === 'error') {
    return (
      <div className={styles.quizContainer}>
        <div className={styles.error}>
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={loadQuiz} className={styles.button}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Render ready state (quiz intro)
  if (state === 'ready' && quizData) {
    return (
      <div className={styles.quizContainer}>
        <div className={styles.intro}>
          <h2>{quizData.title}</h2>
          <div className={styles.quizInfo}>
            <p><strong>Questions:</strong> {quizData.questions.length}</p>
            {quizData.time_limit_minutes && (
              <p><strong>Time Limit:</strong> {quizData.time_limit_minutes} minutes</p>
            )}
            <p><strong>Passing Score:</strong> 70%</p>
          </div>
          <button onClick={startQuiz} className={styles.startButton}>
            Start Quiz
          </button>
        </div>
      </div>
    );
  }

  // Render results state
  if (state === 'results' && result) {
    return (
      <div className={styles.quizContainer}>
        <QuizResults result={result} onRetry={retryQuiz} />
      </div>
    );
  }

  // Render taking quiz state
  if ((state === 'taking' || state === 'submitting') && quizData) {
    return (
      <div className={styles.quizContainer}>
        <div className={styles.quizHeader}>
          <h2>{quizData.title}</h2>
          <div className={styles.progress}>
            <span>{answeredCount} / {totalQuestions} answered</span>
            <div className={styles.progressBar}>
              <div
                className={styles.progressFill}
                style={{ width: `${(answeredCount / totalQuestions) * 100}%` }}
              />
            </div>
          </div>
        </div>

        <div className={styles.questions}>
          {quizData.questions.map((question, index) => (
            <QuizQuestion
              key={question.id}
              question={question}
              questionNumber={index + 1}
              selectedAnswer={answers[question.id] || ''}
              onAnswerChange={(answer) => handleAnswerChange(question.id, answer)}
              disabled={state === 'submitting'}
            />
          ))}
        </div>

        <div className={styles.submitSection}>
          <button
            onClick={submitQuiz}
            disabled={!allAnswered || state === 'submitting'}
            className={`${styles.submitButton} ${allAnswered ? styles.ready : ''}`}
          >
            {state === 'submitting' ? 'Submitting...' : 'Submit Quiz'}
          </button>
          {!allAnswered && (
            <p className={styles.hint}>
              Please answer all questions before submitting.
            </p>
          )}
        </div>
      </div>
    );
  }

  return null;
}
