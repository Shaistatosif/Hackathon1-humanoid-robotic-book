/**
 * QuizQuestion component for displaying individual quiz questions.
 *
 * Supports multiple choice, true/false, and short answer questions.
 */

import React from 'react';
import styles from './styles.module.css';

interface Question {
  id: string;
  question_type: string;
  question_text: string;
  options: string[] | null;
  points: number;
  order: number;
}

interface QuizQuestionProps {
  question: Question;
  questionNumber: number;
  selectedAnswer: string;
  onAnswerChange: (answer: string) => void;
  disabled?: boolean;
}

export default function QuizQuestion({
  question,
  questionNumber,
  selectedAnswer,
  onAnswerChange,
  disabled = false,
}: QuizQuestionProps): JSX.Element {
  const { question_type, question_text, options } = question;

  // Render multiple choice question
  if (question_type === 'multiple_choice' && options) {
    return (
      <div className={styles.question}>
        <div className={styles.questionHeader}>
          <span className={styles.questionNumber}>Q{questionNumber}</span>
          <span className={styles.questionType}>Multiple Choice</span>
        </div>
        <p className={styles.questionText}>{question_text}</p>
        <div className={styles.options}>
          {options.map((option, index) => {
            const optionLetter = String.fromCharCode(65 + index); // A, B, C, D
            const isSelected = selectedAnswer.toUpperCase() === optionLetter;

            return (
              <label
                key={index}
                className={`${styles.option} ${isSelected ? styles.selected : ''}`}
              >
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  value={optionLetter}
                  checked={isSelected}
                  onChange={(e) => onAnswerChange(e.target.value)}
                  disabled={disabled}
                />
                <span className={styles.optionText}>{option}</span>
              </label>
            );
          })}
        </div>
      </div>
    );
  }

  // Render true/false question
  if (question_type === 'true_false') {
    return (
      <div className={styles.question}>
        <div className={styles.questionHeader}>
          <span className={styles.questionNumber}>Q{questionNumber}</span>
          <span className={styles.questionType}>True/False</span>
        </div>
        <p className={styles.questionText}>{question_text}</p>
        <div className={styles.options}>
          {['True', 'False'].map((option) => {
            const isSelected = selectedAnswer === option;

            return (
              <label
                key={option}
                className={`${styles.option} ${isSelected ? styles.selected : ''}`}
              >
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  value={option}
                  checked={isSelected}
                  onChange={(e) => onAnswerChange(e.target.value)}
                  disabled={disabled}
                />
                <span className={styles.optionText}>{option}</span>
              </label>
            );
          })}
        </div>
      </div>
    );
  }

  // Render short answer question
  if (question_type === 'short_answer') {
    return (
      <div className={styles.question}>
        <div className={styles.questionHeader}>
          <span className={styles.questionNumber}>Q{questionNumber}</span>
          <span className={styles.questionType}>Short Answer</span>
        </div>
        <p className={styles.questionText}>{question_text}</p>
        <textarea
          className={styles.shortAnswer}
          value={selectedAnswer}
          onChange={(e) => onAnswerChange(e.target.value)}
          placeholder="Type your answer here..."
          disabled={disabled}
          rows={4}
        />
      </div>
    );
  }

  // Fallback for unknown question types
  return (
    <div className={styles.question}>
      <div className={styles.questionHeader}>
        <span className={styles.questionNumber}>Q{questionNumber}</span>
      </div>
      <p className={styles.questionText}>{question_text}</p>
      <input
        type="text"
        className={styles.textInput}
        value={selectedAnswer}
        onChange={(e) => onAnswerChange(e.target.value)}
        placeholder="Enter your answer..."
        disabled={disabled}
      />
    </div>
  );
}
