/**
 * Register Page
 *
 * LEARNING NOTE:
 * Similar to LoginPage, but for new user registration.
 * Features inline validation with:
 * - Email format check
 * - Password strength meter (weak / medium / strong)
 * - Password confirmation match indicator
 *
 * After successful registration, user is automatically
 * redirected to the intake form.
 */

import { useState, useMemo, useCallback, type FormEvent, type ChangeEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

/** Simple email regex for inline validation */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** Password strength levels */
type StrengthLevel = 'none' | 'weak' | 'medium' | 'strong';

interface PasswordStrength {
  level: StrengthLevel;
  label: string;
  percent: number;
}

/** Calculate password strength */
function getPasswordStrength(pw: string): PasswordStrength {
  if (pw.length === 0) return { level: 'none', label: '', percent: 0 };

  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) score++;
  if (/\d/.test(pw)) score++;
  if (/[^a-zA-Z0-9]/.test(pw)) score++;

  if (score <= 1) return { level: 'weak', label: 'Schwach', percent: 33 };
  if (score <= 3) return { level: 'medium', label: 'Mittel', percent: 66 };
  return { level: 'strong', label: 'Stark', percent: 100 };
}

export default function RegisterPage() {
  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Touch tracking
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Auth store
  const { register, loginWithGoogle, isLoading, error, clearError } = useAuthStore();

  // ── Derived validation ──────────────────────────────────────────────
  const emailError =
    touched.email && email.length > 0 && !EMAIL_REGEX.test(email)
      ? 'Bitte eine gültige E-Mail eingeben'
      : '';

  const passwordStrength = useMemo(() => getPasswordStrength(password), [password]);

  const passwordTooShort =
    touched.password && password.length > 0 && password.length < 8;

  const confirmError =
    touched.confirmPassword &&
    confirmPassword.length > 0 &&
    password !== confirmPassword
      ? 'Passwörter stimmen nicht überein'
      : '';

  const confirmMatch =
    touched.confirmPassword &&
    confirmPassword.length > 0 &&
    password === confirmPassword &&
    password.length >= 8;

  const isFormValid =
    EMAIL_REGEX.test(email) &&
    password.length >= 8 &&
    password === confirmPassword;

  // ── Handlers ────────────────────────────────────────────────────────
  const handleBlur = useCallback((field: string) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
  }, []);

  const handleEmailChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      setEmail(e.target.value);
      if (error) clearError();
    },
    [error, clearError],
  );

  const handlePasswordChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      setPassword(e.target.value);
      if (error) clearError();
    },
    [error, clearError],
  );

  const handleConfirmChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      setConfirmPassword(e.target.value);
      if (error) clearError();
    },
    [error, clearError],
  );

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();

    // Touch all fields on submit
    setTouched({ email: true, password: true, confirmPassword: true });

    if (!isFormValid) return;

    try {
      await register(email, password);
      // Navigation to intake happens automatically via IntakeRoute
    } catch {
      // Error is stored in authStore.error
    }
  };

  const handleGoogleSignup = async () => {
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
        {/* Logo / Header */}
        <div className="auth-logo">
          <h1>Sloth</h1>
          <p>Starte deine Faultierdiät</p>
        </div>

        {/* Server error */}
        {error && (
          <div className="auth-error" role="alert">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="auth-error-icon">
              <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
              <path d="M8 4.5v4M8 10.5v.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
            {error}
          </div>
        )}

        {/* Register form */}
        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          {/* Email */}
          <div className="form-group">
            <label className="form-label" htmlFor="email">
              E-Mail
            </label>
            <input
              id="email"
              type="email"
              className={`form-input${emailError ? ' error' : ''}`}
              placeholder="deine@email.de"
              value={email}
              onChange={handleEmailChange}
              onBlur={() => handleBlur('email')}
              required
              autoComplete="email"
              disabled={isLoading}
              aria-invalid={!!emailError}
              aria-describedby={emailError ? 'reg-email-error' : undefined}
            />
            {emailError && (
              <span id="reg-email-error" className="form-error" role="alert">
                {emailError}
              </span>
            )}
          </div>

          {/* Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="password">
              Passwort
            </label>
            <input
              id="password"
              type="password"
              className={`form-input${passwordTooShort ? ' error' : ''}`}
              placeholder="Mindestens 8 Zeichen"
              value={password}
              onChange={handlePasswordChange}
              onBlur={() => handleBlur('password')}
              required
              minLength={8}
              autoComplete="new-password"
              disabled={isLoading}
              aria-invalid={!!passwordTooShort}
              aria-describedby="password-strength"
            />
            {/* Strength meter */}
            {password.length > 0 && (
              <div className="password-strength" id="password-strength">
                <div className="password-strength-track">
                  <div
                    className={`password-strength-bar strength-${passwordStrength.level}`}
                    style={{ width: `${passwordStrength.percent}%` }}
                  />
                </div>
                <span className={`password-strength-label strength-${passwordStrength.level}`}>
                  {passwordStrength.label}
                </span>
              </div>
            )}
            {passwordTooShort && (
              <span className="form-error" role="alert">
                Mindestens 8 Zeichen erforderlich
              </span>
            )}
          </div>

          {/* Confirm Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="confirmPassword">
              Passwort bestätigen
            </label>
            <input
              id="confirmPassword"
              type="password"
              className={`form-input${confirmError ? ' error' : ''}${confirmMatch ? ' success' : ''}`}
              placeholder="Passwort wiederholen"
              value={confirmPassword}
              onChange={handleConfirmChange}
              onBlur={() => handleBlur('confirmPassword')}
              required
              autoComplete="new-password"
              disabled={isLoading}
              aria-invalid={!!confirmError}
              aria-describedby={
                confirmError
                  ? 'confirm-error'
                  : confirmMatch
                    ? 'confirm-match'
                    : undefined
              }
            />
            {confirmError && (
              <span id="confirm-error" className="form-error" role="alert">
                {confirmError}
              </span>
            )}
            {confirmMatch && (
              <span id="confirm-match" className="form-success" role="status">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style={{ marginRight: 4, verticalAlign: '-2px' }}>
                  <circle cx="7" cy="7" r="6" stroke="currentColor" strokeWidth="1.5" />
                  <path d="M4.5 7l2 2 3-3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Passwörter stimmen überein
              </span>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full btn-lg"
            disabled={isLoading || (!isFormValid && touched.email && touched.password)}
          >
            {isLoading ? (
              <span className="btn-loading">
                <span className="spinner" />
                Registrieren…
              </span>
            ) : (
              'Konto erstellen'
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="auth-divider">
          <span>oder</span>
        </div>

        {/* Google Sign Up Button */}
        <button
          type="button"
          className="btn btn-google btn-full btn-lg"
          onClick={handleGoogleSignup}
          disabled={isLoading}
        >
          <svg className="google-icon" viewBox="0 0 24 24" width="20" height="20">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Mit Google registrieren
        </button>

        {/* Footer */}
        <div className="auth-footer">
          <p>
            Bereits registriert?{' '}
            <Link to="/login">Jetzt anmelden</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
