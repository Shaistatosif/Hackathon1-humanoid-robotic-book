/**
 * ChatWidget component for RAG chatbot interaction.
 *
 * Provides a floating chat interface for asking questions about the textbook.
 * Supports bilingual (English/Urdu) content retrieval.
 */

import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { useHistory, useLocation } from '@docusaurus/router';
import ChatMessage, { Citation, Message } from './ChatMessage';
import styles from './styles.module.css';

// Production API URL - Render deployment
const PRODUCTION_API_URL = 'https://humanoid-robotics-api.onrender.com';
const DEVELOPMENT_API_URL = 'http://localhost:8000';

// Detect environment: production if running on Vercel domain
const isProduction = typeof window !== 'undefined' &&
  (window.location.hostname.includes('vercel.app') ||
   window.location.hostname.includes('hackathon-one-humanoid-robotic-book'));

const API_URL = isProduction ? PRODUCTION_API_URL : DEVELOPMENT_API_URL;

interface QueryResponse {
  answer: string;
  citations: Citation[];
  is_out_of_scope: boolean;
  confidence: number;
  session_id: string;
}

// UI text translations
const UI_TEXT = {
  en: {
    title: 'AI Assistant',
    clear: 'Clear',
    placeholder: 'Ask a question...',
    emptyState: 'Ask me anything about humanoid robotics!',
    thinking: 'Thinking...',
    errorMessage: 'Sorry, I encountered an error. Please try again.',
    suggestions: [
      'What is a humanoid robot?',
      'How do robots maintain balance?',
      'What sensors do humanoid robots use?',
    ],
  },
  ur: {
    title: 'AI معاون',
    clear: 'صاف کریں',
    placeholder: 'سوال پوچھیں...',
    emptyState: 'مجھ سے ہیومنائیڈ روبوٹکس کے بارے میں کچھ بھی پوچھیں!',
    thinking: 'سوچ رہا ہوں...',
    errorMessage: 'معذرت، ایک خرابی ہوئی۔ براہ کرم دوبارہ کوشش کریں۔',
    suggestions: [
      'ہیومنائیڈ روبوٹ کیا ہے؟',
      'روبوٹ توازن کیسے برقرار رکھتے ہیں؟',
      'ہیومنائیڈ روبوٹ کون سے سینسر استعمال کرتے ہیں؟',
    ],
  },
};

function getLocaleFromPath(pathname: string): 'en' | 'ur' {
  const match = pathname.match(/^\/([a-z]{2})(\/|$)/);
  return match && match[1] === 'ur' ? 'ur' : 'en';
}

export default function ChatWidget(): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const history = useHistory();
  const location = useLocation();

  // Detect current language from URL
  const language = useMemo(() => getLocaleFromPath(location.pathname), [location.pathname]);
  const isRTL = language === 'ur';
  const text = UI_TEXT[language];

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const toggleChat = useCallback(() => {
    setIsOpen((prev) => !prev);
    setError(null);
  }, []);

  const handleCitationClick = useCallback(
    (citation: Citation) => {
      // Navigate to the chapter and section, preserving language
      const langPrefix = language === 'ur' ? '/ur' : '';
      const path = `${langPrefix}/${citation.chapter_id}#${citation.section_id}`;
      history.push(path);
      setIsOpen(false);
    },
    [history, language]
  );

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/rag/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage.content,
          session_id: sessionId,
          language: language,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data: QueryResponse = await response.json();

      // Update session ID
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      setError(text.errorMessage);

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: text.errorMessage,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  };

  return (
    <div className={`${styles.chatWidget} ${isRTL ? styles.rtl : ''}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Chat toggle button */}
      <button
        className={styles.toggleButton}
        onClick={toggleChat}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
        title={isRTL ? 'درسی کتاب کے بارے میں سوالات پوچھیں' : 'Ask questions about the textbook'}
      >
        {isOpen ? (
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" />
          </svg>
        )}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className={styles.chatPanel}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <h3>AI Assistant</h3>
            <div className={styles.headerActions}>
              <button
                className={styles.clearButton}
                onClick={clearChat}
                title="Clear chat"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className={styles.messagesContainer}>
            {messages.length === 0 ? (
              <div className={styles.emptyState}>
                <p>Ask me anything about humanoid robotics!</p>
                <div className={styles.suggestions}>
                  <button
                    onClick={() => setInput('What is a humanoid robot?')}
                    className={styles.suggestionButton}
                  >
                    What is a humanoid robot?
                  </button>
                  <button
                    onClick={() => setInput('How do robots maintain balance?')}
                    className={styles.suggestionButton}
                  >
                    How do robots maintain balance?
                  </button>
                  <button
                    onClick={() => setInput('What sensors do humanoid robots use?')}
                    className={styles.suggestionButton}
                  >
                    What sensors do humanoid robots use?
                  </button>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  onCitationClick={handleCitationClick}
                />
              ))
            )}
            {isLoading && (
              <div className={styles.loadingIndicator}>
                <span>Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Error message */}
          {error && <div className={styles.errorMessage}>{error}</div>}

          {/* Input */}
          <div className={styles.inputContainer}>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question..."
              disabled={isLoading}
              className={styles.input}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className={styles.sendButton}
              aria-label="Send message"
            >
              <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
