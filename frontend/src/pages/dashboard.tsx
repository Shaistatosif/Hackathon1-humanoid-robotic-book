/**
 * Dashboard page component.
 *
 * Provides personalized learning dashboard for authenticated users.
 * Shows reading progress, quiz history, bookmarks, and recommendations.
 */

import React, { useEffect, useState } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { useAuth } from '../context/AuthContext';
import { get, del } from '../services/api';
import ProgressCard from '../components/Dashboard/ProgressCard';
import BookmarksList from '../components/Dashboard/BookmarksList';
import QuizHistory from '../components/Dashboard/QuizHistory';
import Recommendations from '../components/Dashboard/Recommendations';
import styles from './dashboard.module.css';

// API Response Types
interface ChapterProgress {
  chapter_id: string;
  status: string;
  progress_percent: number;
  time_spent_seconds: number;
  last_position: number;
  started_at: string | null;
  completed_at: string | null;
}

interface Bookmark {
  id: string;
  chapter_id: string;
  section_id: string | null;
  title: string;
  note: string | null;
  created_at: string;
}

interface QuizAttempt {
  id: string;
  quiz_id: string;
  score: number;
  total_questions: number;
  correct_answers: number;
  completed_at: string | null;
}

interface Recommendation {
  type: string;
  chapter_id: string;
  title: string;
  description: string;
  priority: number;
}

interface DashboardStats {
  completed_chapters: number;
  in_progress_chapters: number;
  total_time_minutes: number;
  total_bookmarks: number;
  quizzes_taken: number;
  average_quiz_score: number;
}

interface DashboardData {
  progress: ChapterProgress[];
  bookmarks: Bookmark[];
  quiz_history: QuizAttempt[];
  stats: DashboardStats;
  recommendations: Recommendation[];
}

export default function DashboardPage(): JSX.Element {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch dashboard data when authenticated
  useEffect(() => {
    async function fetchDashboardData() {
      if (!isAuthenticated) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const data = await get<DashboardData>('/api/user/dashboard');
        setDashboardData(data);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }

    if (!authLoading) {
      fetchDashboardData();
    }
  }, [isAuthenticated, authLoading]);

  // Handle bookmark deletion
  const handleDeleteBookmark = async (bookmarkId: string) => {
    try {
      await del(`/api/user/bookmarks/${bookmarkId}`);
      // Update local state
      if (dashboardData) {
        setDashboardData({
          ...dashboardData,
          bookmarks: dashboardData.bookmarks.filter((b) => b.id !== bookmarkId),
        });
      }
    } catch (err) {
      console.error('Failed to delete bookmark:', err);
    }
  };

  // Loading state
  if (authLoading || isLoading) {
    return (
      <Layout title="Dashboard" description="Your personalized learning dashboard">
        <main className={styles.container}>
          <div className={styles.loading}>
            <div className={styles.spinner} />
            <p>Loading your dashboard...</p>
          </div>
        </main>
      </Layout>
    );
  }

  // Not authenticated
  if (!isAuthenticated) {
    return (
      <Layout title="Dashboard" description="Your personalized learning dashboard">
        <main className={styles.container}>
          <div className={styles.authPrompt}>
            <h1>Welcome to Your Dashboard</h1>
            <p>Sign in to track your learning progress and access personalized features.</p>
            <div className={styles.authButtons}>
              <Link to="/login" className="button button--primary button--lg">
                Sign In
              </Link>
              <Link to="/register" className="button button--outline button--primary button--lg">
                Create Account
              </Link>
            </div>
          </div>
        </main>
      </Layout>
    );
  }

  // Error state or backend unavailable
  if (error || (!dashboardData && !isLoading)) {
    return (
      <Layout title="Dashboard" description="Your personalized learning dashboard">
        <main className={styles.container}>
          <div className={styles.header}>
            <h1>Dashboard</h1>
          </div>
          <div className={styles.error}>
            <h2>Backend Not Available</h2>
            <p>The dashboard requires a backend server which is not currently deployed.</p>
            <p>You can still browse the textbook content:</p>
            <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <Link to="/chapter-1" className="button button--primary">
                Read Chapter 1
              </Link>
              <Link to="/chapter-2" className="button button--secondary">
                Read Chapter 2
              </Link>
              <Link to="/chapter-3" className="button button--secondary">
                Read Chapter 3
              </Link>
            </div>
          </div>
        </main>
      </Layout>
    );
  }

  // Success state with data
  const progress = dashboardData?.progress || [];
  const bookmarks = dashboardData?.bookmarks || [];
  const quizHistory = dashboardData?.quiz_history || [];
  const recommendations = dashboardData?.recommendations || [];
  const stats = dashboardData?.stats;

  return (
    <Layout title="Dashboard" description="Your personalized learning dashboard">
      <main className={styles.container}>
        <div className={styles.header}>
          <h1>Welcome back, {user?.display_name || user?.email}</h1>
          <p>Track your progress and continue learning humanoid robotics.</p>
        </div>

        {/* Stats Summary */}
        {stats && (
          <div className={styles.statsRow}>
            <div className={styles.stat}>
              <span className={styles.statValue}>{stats.completed_chapters}</span>
              <span className={styles.statLabel}>Chapters Completed</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>{stats.total_time_minutes}</span>
              <span className={styles.statLabel}>Minutes Reading</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>{stats.quizzes_taken}</span>
              <span className={styles.statLabel}>Quizzes Taken</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>
                {stats.average_quiz_score > 0 ? `${stats.average_quiz_score}%` : '-'}
              </span>
              <span className={styles.statLabel}>Avg Quiz Score</span>
            </div>
          </div>
        )}

        {/* Main Grid */}
        <div className={styles.grid}>
          {/* Progress Card */}
          <ProgressCard progress={progress} totalChapters={3} />

          {/* Quiz History */}
          <QuizHistory attempts={quizHistory} />

          {/* Bookmarks */}
          <BookmarksList bookmarks={bookmarks} onDelete={handleDeleteBookmark} />

          {/* Recommendations */}
          <Recommendations recommendations={recommendations} />
        </div>
      </main>
    </Layout>
  );
}
