/**
 * Hook for tracking reading progress on chapter pages.
 *
 * Automatically tracks scroll position, time spent, and progress percentage.
 * Sends updates to the backend API for authenticated users.
 */

import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { post } from '../services/api';

interface ReadingProgressOptions {
  /** Chapter identifier (e.g., "chapter-1") */
  chapterId: string;
  /** Minimum time between API updates in milliseconds (default: 30000) */
  updateInterval?: number;
  /** Scroll threshold for progress calculation (default: 0.9 for 90%) */
  completionThreshold?: number;
}

interface ProgressUpdate {
  chapter_id: string;
  progress_percent: number;
  time_spent_seconds: number;
  last_position: number;
}

/**
 * Track reading progress for a chapter.
 *
 * @param options - Configuration options
 * @returns Object with manual update function
 *
 * @example
 * ```tsx
 * function ChapterPage({ chapterId }) {
 *   const { updateProgress } = useReadingProgress({ chapterId });
 *
 *   // Progress is tracked automatically via scroll events
 *   // Call updateProgress() manually if needed
 * }
 * ```
 */
export function useReadingProgress({
  chapterId,
  updateInterval = 30000,
  completionThreshold = 0.9,
}: ReadingProgressOptions) {
  const { isAuthenticated } = useAuth();
  const startTime = useRef<number>(Date.now());
  const lastUpdateTime = useRef<number>(0);
  const maxProgress = useRef<number>(0);
  const totalTimeSpent = useRef<number>(0);
  const isVisible = useRef<boolean>(true);
  const lastVisibilityChange = useRef<number>(Date.now());

  /**
   * Calculate current scroll progress as percentage (0-100).
   */
  const calculateProgress = useCallback((): number => {
    if (typeof window === 'undefined') return 0;

    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;

    if (docHeight <= 0) return 100;

    const progress = Math.min((scrollTop / docHeight) * 100, 100);
    return Math.round(progress);
  }, []);

  /**
   * Get current scroll position as a decimal (0-1).
   */
  const getScrollPosition = useCallback((): number => {
    if (typeof window === 'undefined') return 0;

    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;

    if (docHeight <= 0) return 1;

    return Math.min(scrollTop / docHeight, 1);
  }, []);

  /**
   * Calculate time spent reading (accounts for tab visibility).
   */
  const calculateTimeSpent = useCallback((): number => {
    const now = Date.now();
    if (isVisible.current) {
      totalTimeSpent.current += (now - lastVisibilityChange.current) / 1000;
    }
    lastVisibilityChange.current = now;
    return Math.round(totalTimeSpent.current);
  }, []);

  /**
   * Send progress update to the API.
   */
  const sendProgressUpdate = useCallback(
    async (force = false): Promise<void> => {
      if (!isAuthenticated) return;

      const now = Date.now();
      if (!force && now - lastUpdateTime.current < updateInterval) return;

      const currentProgress = calculateProgress();
      maxProgress.current = Math.max(maxProgress.current, currentProgress);

      const update: ProgressUpdate = {
        chapter_id: chapterId,
        progress_percent: maxProgress.current,
        time_spent_seconds: calculateTimeSpent(),
        last_position: getScrollPosition(),
      };

      try {
        await post('/api/user/progress', update);
        lastUpdateTime.current = now;
      } catch (err) {
        console.error('Failed to update reading progress:', err);
      }
    },
    [
      isAuthenticated,
      chapterId,
      updateInterval,
      calculateProgress,
      calculateTimeSpent,
      getScrollPosition,
    ]
  );

  /**
   * Manual update function for external use.
   */
  const updateProgress = useCallback(() => {
    sendProgressUpdate(true);
  }, [sendProgressUpdate]);

  // Track scroll events
  useEffect(() => {
    if (typeof window === 'undefined') return;

    let scrollTimeout: NodeJS.Timeout;

    const handleScroll = () => {
      // Update max progress
      const currentProgress = calculateProgress();
      maxProgress.current = Math.max(maxProgress.current, currentProgress);

      // Debounce API updates
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        sendProgressUpdate();
      }, 1000);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      window.removeEventListener('scroll', handleScroll);
      clearTimeout(scrollTimeout);
    };
  }, [calculateProgress, sendProgressUpdate]);

  // Track visibility changes
  useEffect(() => {
    if (typeof document === 'undefined') return;

    const handleVisibilityChange = () => {
      const wasVisible = isVisible.current;
      isVisible.current = !document.hidden;

      if (wasVisible && !isVisible.current) {
        // Page became hidden - save time spent
        totalTimeSpent.current += (Date.now() - lastVisibilityChange.current) / 1000;
        lastVisibilityChange.current = Date.now();
        // Send update when leaving
        sendProgressUpdate(true);
      } else if (!wasVisible && isVisible.current) {
        // Page became visible - reset visibility timer
        lastVisibilityChange.current = Date.now();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [sendProgressUpdate]);

  // Track time and send periodic updates
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const intervalId = setInterval(() => {
      if (isVisible.current && isAuthenticated) {
        sendProgressUpdate();
      }
    }, updateInterval);

    return () => {
      clearInterval(intervalId);
    };
  }, [sendProgressUpdate, updateInterval, isAuthenticated]);

  // Send final update on unmount
  useEffect(() => {
    return () => {
      sendProgressUpdate(true);
    };
  }, [sendProgressUpdate]);

  // Mark as complete if user scrolls past threshold
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const checkCompletion = () => {
      const position = getScrollPosition();
      if (position >= completionThreshold) {
        maxProgress.current = 100;
        sendProgressUpdate(true);
      }
    };

    window.addEventListener('scroll', checkCompletion, { passive: true });

    return () => {
      window.removeEventListener('scroll', checkCompletion);
    };
  }, [getScrollPosition, completionThreshold, sendProgressUpdate]);

  return {
    updateProgress,
    getProgress: () => maxProgress.current,
    getTimeSpent: () => calculateTimeSpent(),
  };
}

export default useReadingProgress;
