/**
 * Reusable Loading component with accessibility support.
 *
 * Provides consistent loading indicators across the application.
 */

import React from 'react';
import styles from './styles.module.css';

interface LoadingProps {
  /** Loading message to display */
  message?: string;
  /** Size variant */
  size?: 'small' | 'medium' | 'large';
  /** Whether to show as inline or full container */
  inline?: boolean;
  /** Custom className */
  className?: string;
}

/**
 * Loading spinner component.
 *
 * @example
 * ```tsx
 * // Simple spinner
 * <Loading />
 *
 * // With message
 * <Loading message="Loading chapters..." />
 *
 * // Inline small spinner
 * <Loading size="small" inline />
 * ```
 */
export default function Loading({
  message = 'Loading...',
  size = 'medium',
  inline = false,
  className = '',
}: LoadingProps): JSX.Element {
  const sizeClass = styles[size];

  if (inline) {
    return (
      <span
        className={`${styles.inlineContainer} ${className}`}
        role="status"
        aria-live="polite"
      >
        <span
          className={`${styles.spinner} ${sizeClass}`}
          aria-hidden="true"
        />
        <span className={styles.srOnly}>{message}</span>
      </span>
    );
  }

  return (
    <div
      className={`${styles.container} ${className}`}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <div
        className={`${styles.spinner} ${sizeClass}`}
        aria-hidden="true"
      />
      {message && (
        <p className={styles.message}>{message}</p>
      )}
      <span className={styles.srOnly}>{message}</span>
    </div>
  );
}

/**
 * Skeleton loading placeholder for content.
 */
export function Skeleton({
  width = '100%',
  height = '1rem',
  borderRadius = '4px',
  className = '',
}: {
  width?: string;
  height?: string;
  borderRadius?: string;
  className?: string;
}): JSX.Element {
  return (
    <div
      className={`${styles.skeleton} ${className}`}
      style={{ width, height, borderRadius }}
      aria-hidden="true"
    />
  );
}

/**
 * Loading overlay for sections.
 */
export function LoadingOverlay({
  message = 'Loading...',
  visible = true,
}: {
  message?: string;
  visible?: boolean;
}): JSX.Element | null {
  if (!visible) return null;

  return (
    <div
      className={styles.overlay}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <div className={styles.overlayContent}>
        <div className={`${styles.spinner} ${styles.large}`} aria-hidden="true" />
        <p className={styles.message}>{message}</p>
      </div>
    </div>
  );
}
