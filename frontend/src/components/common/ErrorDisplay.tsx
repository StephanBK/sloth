/**
 * Error Display Components
 *
 * Consistent error messaging across the app.
 */

import type { ReactNode } from 'react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  className?: string;
}

/**
 * Inline error message
 */
export function ErrorMessage({ message, onRetry, className = '' }: ErrorMessageProps) {
  return (
    <div className={`error-message ${className}`} role="alert">
      <span className="error-icon">!</span>
      <span className="error-text">{message}</span>
      {onRetry && (
        <button type="button" className="error-retry-btn" onClick={onRetry}>
          Erneut versuchen
        </button>
      )}
    </div>
  );
}

/**
 * Error state for empty content areas
 */
interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  icon?: ReactNode;
}

export function ErrorState({
  title = 'Ein Fehler ist aufgetreten',
  message,
  onRetry,
  icon,
}: ErrorStateProps) {
  return (
    <div className="error-state">
      {icon && <div className="error-state-icon">{icon}</div>}
      <h3 className="error-state-title">{title}</h3>
      <p className="error-state-message">{message}</p>
      {onRetry && (
        <button type="button" className="btn btn-secondary" onClick={onRetry}>
          Erneut versuchen
        </button>
      )}
    </div>
  );
}

/**
 * Empty state for lists with no data
 */
interface EmptyStateProps {
  title: string;
  message?: string;
  action?: ReactNode;
  icon?: ReactNode;
}

export function EmptyState({ title, message, action, icon }: EmptyStateProps) {
  return (
    <div className="empty-state">
      {icon && <div className="empty-state-icon">{icon}</div>}
      <h3 className="empty-state-title">{title}</h3>
      {message && <p className="empty-state-message">{message}</p>}
      {action && <div className="empty-state-action">{action}</div>}
    </div>
  );
}

export default ErrorMessage;
