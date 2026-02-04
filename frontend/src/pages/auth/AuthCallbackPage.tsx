/**
 * OAuth Callback Page
 *
 * This page handles the redirect from Google OAuth.
 * After successful Google authentication, Supabase redirects here
 * with access tokens in the URL hash.
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

export default function AuthCallbackPage() {
  const navigate = useNavigate();
  const { handleOAuthCallback, isAuthenticated } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const processCallback = async () => {
      // Check if there's an error in the URL
      const params = new URLSearchParams(window.location.hash.substring(1));
      const errorMsg = params.get('error_description') || params.get('error');

      if (errorMsg) {
        setError(errorMsg);
        return;
      }

      // Process the OAuth callback
      const success = await handleOAuthCallback();

      if (success) {
        // Clear the hash from URL for cleaner history
        window.history.replaceState(null, '', window.location.pathname);
      } else {
        setError('Anmeldung fehlgeschlagen. Bitte versuche es erneut.');
      }
    };

    processCallback();
  }, [handleOAuthCallback]);

  // Redirect when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  if (error) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="auth-logo">
            <h1>Sloth</h1>
            <p>Anmeldung fehlgeschlagen</p>
          </div>
          <div className="auth-error">{error}</div>
          <button
            className="btn btn-primary btn-full btn-lg"
            onClick={() => navigate('/login')}
          >
            Zurück zum Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <h1>Sloth</h1>
          <p>Anmeldung wird verarbeitet...</p>
        </div>
        <div className="loading-container" style={{ minHeight: '100px' }}>
          <div className="loading-spinner"></div>
        </div>
      </div>
    </div>
  );
}
