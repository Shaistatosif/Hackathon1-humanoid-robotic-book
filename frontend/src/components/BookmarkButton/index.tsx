/**
 * BookmarkButton component for chapter pages.
 *
 * Allows authenticated users to bookmark chapters and sections.
 * Shows bookmark status and toggles bookmarked state.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { get, post, del } from '../../services/api';
import styles from './styles.module.css';

interface BookmarkButtonProps {
  /** Chapter identifier (e.g., "chapter-1") */
  chapterId: string;
  /** Optional section anchor within the chapter */
  sectionId?: string;
  /** Display title for the bookmark */
  title: string;
  /** Button variant */
  variant?: 'icon' | 'text' | 'full';
  /** Optional className for styling */
  className?: string;
}

interface Bookmark {
  id: string;
  chapter_id: string;
  section_id: string | null;
  title: string;
  note: string | null;
  position: number;
  created_at: string;
}

/**
 * Bookmark button for saving chapters/sections.
 *
 * @example
 * ```tsx
 * // Icon-only button
 * <BookmarkButton chapterId="chapter-1" title="Introduction" />
 *
 * // Full button with text
 * <BookmarkButton
 *   chapterId="chapter-1"
 *   sectionId="sensors"
 *   title="Sensors Section"
 *   variant="full"
 * />
 * ```
 */
export default function BookmarkButton({
  chapterId,
  sectionId,
  title,
  variant = 'icon',
  className = '',
}: BookmarkButtonProps): JSX.Element {
  const { isAuthenticated } = useAuth();
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [bookmarkId, setBookmarkId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  // Check if already bookmarked on mount
  useEffect(() => {
    async function checkBookmark() {
      if (!isAuthenticated) return;

      try {
        const bookmarks = await get<Bookmark[]>('/api/user/bookmarks');
        const existing = bookmarks.find(
          (b) =>
            b.chapter_id === chapterId &&
            (sectionId ? b.section_id === sectionId : !b.section_id)
        );

        if (existing) {
          setIsBookmarked(true);
          setBookmarkId(existing.id);
        }
      } catch (err) {
        console.error('Failed to check bookmark status:', err);
      }
    }

    checkBookmark();
  }, [isAuthenticated, chapterId, sectionId]);

  // Get current scroll position
  const getScrollPosition = useCallback((): number => {
    if (typeof window === 'undefined') return 0;

    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;

    if (docHeight <= 0) return 0;

    return Math.min(scrollTop / docHeight, 1);
  }, []);

  // Toggle bookmark
  const handleClick = async () => {
    if (!isAuthenticated) {
      // Show tooltip to encourage sign in
      setShowTooltip(true);
      setTimeout(() => setShowTooltip(false), 3000);
      return;
    }

    setIsLoading(true);

    try {
      if (isBookmarked && bookmarkId) {
        // Remove bookmark
        await del(`/api/user/bookmarks/${bookmarkId}`);
        setIsBookmarked(false);
        setBookmarkId(null);
      } else {
        // Create bookmark
        const bookmark = await post<Bookmark>('/api/user/bookmarks', {
          chapter_id: chapterId,
          section_id: sectionId || null,
          title,
          position: getScrollPosition(),
        });
        setIsBookmarked(true);
        setBookmarkId(bookmark.id);
      }
    } catch (err) {
      console.error('Failed to toggle bookmark:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Render icon-only variant
  if (variant === 'icon') {
    return (
      <div className={`${styles.container} ${className}`}>
        <button
          className={`${styles.iconButton} ${isBookmarked ? styles.bookmarked : ''}`}
          onClick={handleClick}
          disabled={isLoading}
          aria-label={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
          title={isBookmarked ? 'Remove bookmark' : 'Bookmark this page'}
        >
          {isLoading ? (
            <span className={styles.spinner} />
          ) : (
            <span className={styles.icon}>{isBookmarked ? '★' : '☆'}</span>
          )}
        </button>
        {showTooltip && (
          <div className={styles.tooltip}>Sign in to bookmark</div>
        )}
      </div>
    );
  }

  // Render text variant
  if (variant === 'text') {
    return (
      <div className={`${styles.container} ${className}`}>
        <button
          className={`${styles.textButton} ${isBookmarked ? styles.bookmarked : ''}`}
          onClick={handleClick}
          disabled={isLoading}
        >
          {isLoading ? (
            'Saving...'
          ) : isBookmarked ? (
            'Bookmarked'
          ) : (
            'Bookmark'
          )}
        </button>
        {showTooltip && (
          <div className={styles.tooltip}>Sign in to bookmark</div>
        )}
      </div>
    );
  }

  // Render full variant with icon and text
  return (
    <div className={`${styles.container} ${className}`}>
      <button
        className={`${styles.fullButton} ${isBookmarked ? styles.bookmarked : ''}`}
        onClick={handleClick}
        disabled={isLoading}
      >
        <span className={styles.icon}>{isBookmarked ? '★' : '☆'}</span>
        <span className={styles.buttonText}>
          {isLoading ? 'Saving...' : isBookmarked ? 'Bookmarked' : 'Bookmark'}
        </span>
      </button>
      {showTooltip && (
        <div className={styles.tooltip}>Sign in to bookmark</div>
      )}
    </div>
  );
}
