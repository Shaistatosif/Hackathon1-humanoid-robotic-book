/**
 * Summary component displaying AI-generated chapter summaries.
 *
 * Shows overview, key concepts, and takeaways in an organized format.
 */

import React, { useEffect, useState } from 'react';
import { get } from '../../services/api';
import styles from './styles.module.css';

interface KeyConcept {
  concept: string;
  explanation: string;
}

interface ChapterSummary {
  chapter_id: string;
  title: string;
  overview: string;
  key_concepts: KeyConcept[];
  takeaways: string[];
}

interface SummaryProps {
  chapterId: string;
  collapsed?: boolean;
}

type SummaryState = 'loading' | 'loaded' | 'error' | 'not_found';

export default function Summary({
  chapterId,
  collapsed = false,
}: SummaryProps): JSX.Element | null {
  const [state, setState] = useState<SummaryState>('loading');
  const [summary, setSummary] = useState<ChapterSummary | null>(null);
  const [error, setError] = useState<string>('');
  const [isExpanded, setIsExpanded] = useState(!collapsed);

  useEffect(() => {
    const fetchSummary = async () => {
      setState('loading');
      try {
        const data = await get<ChapterSummary>(
          `/api/content/summaries/${chapterId}`
        );
        setSummary(data);
        setState('loaded');
      } catch (err: unknown) {
        if (err && typeof err === 'object' && 'status' in err && err.status === 404) {
          setState('not_found');
        } else {
          setError(err instanceof Error ? err.message : 'Failed to load summary');
          setState('error');
        }
      }
    };

    fetchSummary();
  }, [chapterId]);

  if (state === 'loading') {
    return (
      <div className={styles.summary}>
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <span>Loading summary...</span>
        </div>
      </div>
    );
  }

  if (state === 'not_found') {
    return (
      <div className={styles.summary}>
        <div className={styles.notFound}>
          <span className={styles.icon}>📋</span>
          <p>Summary not available for this chapter yet.</p>
        </div>
      </div>
    );
  }

  if (state === 'error') {
    return (
      <div className={styles.summary}>
        <div className={styles.error}>
          <span className={styles.icon}>⚠️</span>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  return (
    <div className={styles.summary}>
      <button
        className={styles.header}
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <span className={styles.headerIcon}>📝</span>
        <span className={styles.headerTitle}>Chapter Summary</span>
        <span className={`${styles.expandIcon} ${isExpanded ? styles.expanded : ''}`}>
          ▼
        </span>
      </button>

      {isExpanded && (
        <div className={styles.content}>
          {/* Overview Section */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Overview</h3>
            <p className={styles.overview}>{summary.overview}</p>
          </section>

          {/* Key Concepts Section */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Key Concepts</h3>
            <ul className={styles.conceptList}>
              {summary.key_concepts.map((item, index) => (
                <li key={index} className={styles.conceptItem}>
                  <strong className={styles.conceptName}>{item.concept}</strong>
                  <span className={styles.conceptExplanation}>
                    {item.explanation}
                  </span>
                </li>
              ))}
            </ul>
          </section>

          {/* Takeaways Section */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Key Takeaways</h3>
            <ul className={styles.takeawayList}>
              {summary.takeaways.map((takeaway, index) => (
                <li key={index} className={styles.takeawayItem}>
                  <span className={styles.checkmark}>✓</span>
                  {takeaway}
                </li>
              ))}
            </ul>
          </section>
        </div>
      )}
    </div>
  );
}
