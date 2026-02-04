/**
 * Loading Spinner Component
 *
 * Reusable loading indicator with size variants.
 */

type SpinnerSize = 'sm' | 'md' | 'lg';

interface LoadingSpinnerProps {
  size?: SpinnerSize;
  className?: string;
  label?: string;
}

const sizeClasses: Record<SpinnerSize, string> = {
  sm: 'loading-spinner-small',
  md: 'loading-spinner',
  lg: 'loading-spinner-large',
};

export function LoadingSpinner({ size = 'md', className = '', label }: LoadingSpinnerProps) {
  return (
    <div className={`loading-spinner-wrapper ${className}`} role="status" aria-label={label || 'Loading'}>
      <div className={sizeClasses[size]}></div>
      {label && <span className="loading-label">{label}</span>}
    </div>
  );
}

/**
 * Full page loading state
 */
export function LoadingPage({ message = 'Laden...' }: { message?: string }) {
  return (
    <div className="loading-container">
      <LoadingSpinner size="lg" label={message} />
    </div>
  );
}

/**
 * Skeleton loader for content placeholders
 */
interface SkeletonProps {
  width?: string;
  height?: string;
  className?: string;
  variant?: 'text' | 'circle' | 'rect';
}

export function Skeleton({ width, height, className = '', variant = 'text' }: SkeletonProps) {
  const variantClass = variant === 'circle' ? 'skeleton-circle' : variant === 'rect' ? 'skeleton-rect' : '';

  return (
    <div
      className={`skeleton ${variantClass} ${className}`}
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}

export default LoadingSpinner;
