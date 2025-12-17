/**
 * ChatMessage component for displaying individual messages.
 *
 * Renders user and assistant messages with citation links.
 */

import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

export interface Citation {
  chapter_id: string;
  chapter_title: string;
  section_id: string;
  section_title: string;
  text: string;
  relevance_score: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  created_at?: string;
}

interface ChatMessageProps {
  message: Message;
  onCitationClick?: (citation: Citation) => void;
}

export default function ChatMessage({
  message,
  onCitationClick,
}: ChatMessageProps): JSX.Element {
  const isUser = message.role === 'user';

  const handleCitationClick = (citation: Citation) => {
    if (onCitationClick) {
      onCitationClick(citation);
    }
  };

  return (
    <div
      className={`${styles.message} ${isUser ? styles.userMessage : styles.assistantMessage}`}
    >
      <div className={styles.messageHeader}>
        <span className={styles.role}>{isUser ? 'You' : 'Assistant'}</span>
      </div>
      <div className={styles.messageContent}>
        {message.content}
      </div>
      {!isUser && message.citations && message.citations.length > 0 && (
        <div className={styles.citations}>
          <span className={styles.citationsLabel}>Sources:</span>
          <div className={styles.citationList}>
            {message.citations.map((citation, index) => (
              <button
                key={index}
                className={styles.citationButton}
                onClick={() => handleCitationClick(citation)}
                title={`${citation.chapter_title} - ${citation.section_title}`}
              >
                <Link
                  to={`/${citation.chapter_id}#${citation.section_id}`}
                  className={styles.citationLink}
                  onClick={(e) => e.stopPropagation()}
                >
                  {citation.chapter_title.replace('Chapter ', 'Ch. ')}
                </Link>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
