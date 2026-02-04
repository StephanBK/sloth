/**
 * Login Page
 *
 * LEARNING NOTE:
 * This is a controlled form in React.
 * - useState manages form input values
 * - onChange updates state on each keystroke
 * - onSubmit handles form submission
 *
 * We use the authStore for login logic and error handling.
 *
 * TUTORIAL: https://react.dev/reference/react-dom/components/form
 */

import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

export default function LoginPage() {
  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Auth store
  const { login, loginWithGoogle, isLoading, error, clearError } = useAuthStore();

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      await login(email, password);
      // Navigation happens automatically via ProtectedRoute
    } catch {
      // Error is stored in authStore.error
    }
  };

  /**
   * Handle Google login
   */
  const handleGoogleLogin = async () => {
    clearError();
    try {
      await loginWithGoogle();
      // User will be redirected to Google
    } catch {
      // Error is stored in authStore.error
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Logo/Header */}
        <div className="auth-logo">
          <h1>Sloth</h1>
          <p>Willkommen zurück!</p>
        </div>

        {/* Error message */}
        {error && <div className="auth-error">{error}</div>}

        {/* Login form */}
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="email">
              E-Mail
            </label>
            <input
              id="email"
              type="email"
              className="form-input"
              placeholder="deine@email.de"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">
              Passwort
            </label>
            <input
              id="password"
              type="password"
              className="form-input"
              placeholder="Dein Passwort"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full btn-lg"
            disabled={isLoading}
          >
            {isLoading ? 'Anmelden...' : 'Anmelden'}
          </button>
        </form>

        {/* Divider */}
        <div className="auth-divider">
          <span>oder</span>
        </div>

        {/* Google Login Button */}
        <button
          type="button"
          className="btn btn-google btn-full btn-lg"
          onClick={handleGoogleLogin}
          disabled={isLoading}
        >
          <svg className="google-icon" viewBox="0 0 24 24" width="20" height="20">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Mit Google anmelden
        </button>

        {/* Footer links */}
        <div className="auth-footer">
          <p>
            Noch kein Konto?{' '}
            <Link to="/register">Jetzt registrieren</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
