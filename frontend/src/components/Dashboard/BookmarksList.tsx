/**
 * BookmarksList component displaying user's saved bookmarks.
 *
 * Shows bookmarked chapters and sections with quick navigation.
 */

import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

interface Bookmark {
  id: string;
  chapter_id: string;
  section_id: string | null;
  title: string;
  note: string | null;
  created_at: string;
}

interface BookmarksListProps {
  bookmarks: Bookmark[];
  onDelete?: (bookmarkId: string) => void;
}

const chapterTitles: Record<string, string> = {
  'chapter-1': 'Chapter 1',
  'chapter-2': 'Chapter 2',
  'chapter-3': 'Chapter 3',
};

function formatDate(isoDate: string): string {
  const date = new Date(isoDate);
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  });
}

export default function BookmarksList({
  bookmarks,
  onDelete,
}: BookmarksListProps): JSX.Element {
  if (bookmarks.length === 0) {
    return (
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h3 className={styles.cardTitle}>Bookmarks</h3>
        </div>
        <div className={styles.emptyState}>
          <span className={styles.emptyIcon}>🔖</span>
          <p>No bookmarks yet</p>
          <span className={styles.emptyHint}>
            Save your place while reading chapters
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h3 className={styles.cardTitle}>Bookmarks</h3>
        <span className={styles.count}>{bookmarks.length}</span>
      </div>

      <ul className={styles.bookmarkList}>
        {bookmarks.map((bookmark) => {
          const url = bookmark.section_id
            ? `/${bookmark.chapter_id}#${bookmark.section_id}`
            : `/${bookmark.chapter_id}`;

          return (
            <li key={bookmark.id} className={styles.bookmarkItem}>
              <Link to={url} className={styles.bookmarkLink}>
                <span className={styles.bookmarkIcon}>🔖</span>
                <div className={styles.bookmarkContent}>
                  <span className={styles.bookmarkTitle}>{bookmark.title}</span>
                  <span className={styles.bookmarkMeta}>
                    {chapterTitles[bookmark.chapter_id] || bookmark.chapter_id}
                    {' • '}
                    {formatDate(bookmark.created_at)}
                  </span>
                  {bookmark.note && (
                    <span className={styles.bookmarkNote}>{bookmark.note}</span>
                  )}
                </div>
              </Link>
              {onDelete && (
                <button
                  className={styles.deleteButton}
                  onClick={(e) => {
                    e.preventDefault();
                    onDelete(bookmark.id);
                  }}
                  aria-label="Delete bookmark"
                >
                  ×
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
