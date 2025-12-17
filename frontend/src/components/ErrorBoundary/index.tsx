/**
 * Error Boundary component for catching and displaying React errors.
 *
 * Wraps components to gracefully handle runtime errors and display
 * user-friendly error messages instead of crashing the entire app.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import styles from './styles.module.css';

interface ErrorBoundaryProps {
  /** Child components to wrap */
  children: ReactNode;
  /** Optional fallback UI to display on error */
  fallback?: ReactNode;
  /** Optional callback when error occurs */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Component name for error reporting */
  componentName?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary wrapper component.
 *
 * @example
 * ```tsx
 * <ErrorBoundary componentName="QuizWidget">
 *   <Quiz chapterId="chapter-1" />
 * </ErrorBoundary>
 * ```
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so next render shows fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Update state with error info
    this.setState({ errorInfo });

    // Call optional error callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log to external service in production
    if (process.env.NODE_ENV === 'production') {
      // Could integrate with error tracking service here
      // e.g., Sentry, LogRocket, etc.
    }
  }

  handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback, componentName } = this.props;

    if (hasError) {
      // Return custom fallback if provided
      if (fallback) {
        return fallback;
      }

      // Default error UI
      return (
        <div className={styles.errorContainer} role="alert" aria-live="assertive">
          <div className={styles.errorIcon} aria-hidden="true">
            ⚠️
          </div>
          <h2 className={styles.errorTitle}>Something went wrong</h2>
          <p className={styles.errorMessage}>
            {componentName
              ? `An error occurred in the ${componentName} component.`
              : 'An unexpected error occurred.'}
          </p>

          {process.env.NODE_ENV === 'development' && error && (
            <details className={styles.errorDetails}>
              <summary>Error Details</summary>
              <pre className={styles.errorStack}>
                {error.toString()}
                {errorInfo?.componentStack}
              </pre>
            </details>
          )}

          <button
            className={styles.retryButton}
            onClick={this.handleRetry}
            type="button"
          >
            Try Again
          </button>
        </div>
      );
    }

    return children;
  }
}

export default ErrorBoundary;

/**
 * Higher-order component to wrap a component with ErrorBoundary.
 *
 * @example
 * ```tsx
 * const SafeQuiz = withErrorBoundary(Quiz, 'Quiz');
 * ```
 */
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName?: string
): React.FC<P> {
  const WithErrorBoundary: React.FC<P> = (props) => (
    <ErrorBoundary componentName={componentName}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  );

  WithErrorBoundary.displayName = `withErrorBoundary(${
    WrappedComponent.displayName || WrappedComponent.name || 'Component'
  })`;

  return WithErrorBoundary;
}
