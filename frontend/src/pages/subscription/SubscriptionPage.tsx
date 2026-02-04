/**
 * Subscription Page
 *
 * Shows pricing plans and handles subscription management.
 * - View available plans (monthly/yearly)
 * - Current subscription status
 * - Manage subscription (cancel, reactivate)
 * - Promo code input
 */

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  subscriptionApi,
  type SubscriptionPlan,
  type SubscriptionStatus,
} from '@/services/api';

interface SubscriptionInfo {
  status: SubscriptionStatus;
  plan?: SubscriptionPlan;
  current_period_end?: string;
  cancel_at_period_end: boolean;
}

export default function SubscriptionPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [promoCode, setPromoCode] = useState('');
  const [promoValid, setPromoValid] = useState<boolean | null>(null);
  const [promoMessage, setPromoMessage] = useState('');

  // Check for success/cancelled params
  const isSuccess = searchParams.get('session_id') !== null;
  const isCancelled = searchParams.has('cancelled');

  // Fetch subscription status on load
  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      const status = await subscriptionApi.getStatus();
      setSubscription(status);
    } catch (err) {
      console.error('Failed to fetch subscription:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubscribe = async (plan: SubscriptionPlan) => {
    setIsProcessing(true);
    setError(null);

    try {
      const { checkout_url } = await subscriptionApi.createCheckout(
        plan,
        promoValid ? promoCode : undefined
      );
      // Redirect to Stripe Checkout
      window.location.href = checkout_url;
    } catch (err: unknown) {
      let message = 'Fehler beim Erstellen der Checkout-Session';
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        message = axiosErr.response?.data?.detail || message;
      }
      setError(message);
      setIsProcessing(false);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Möchtest du dein Abo wirklich kündigen?')) return;

    setIsProcessing(true);
    setError(null);

    try {
      const status = await subscriptionApi.cancel(true);
      setSubscription(status);
    } catch (err) {
      setError('Fehler beim Kündigen des Abos');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReactivate = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      const status = await subscriptionApi.reactivate();
      setSubscription(status);
    } catch (err) {
      setError('Fehler beim Reaktivieren des Abos');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleManage = async () => {
    setIsProcessing(true);
    try {
      const url = await subscriptionApi.getPortalUrl();
      window.location.href = url;
    } catch (err) {
      setError('Fehler beim Öffnen des Kundenportals');
      setIsProcessing(false);
    }
  };

  const validatePromo = async () => {
    if (!promoCode.trim()) return;

    try {
      const result = await subscriptionApi.validatePromoCode(promoCode);
      setPromoValid(result.valid);
      setPromoMessage(result.message);
    } catch (err) {
      setPromoValid(false);
      setPromoMessage('Fehler bei der Validierung');
    }
  };

  const isActive =
    subscription?.status === 'active' || subscription?.status === 'trialing';

  if (isLoading) {
    return (
      <div className="subscription-page">
        <div className="page-loading">
          <div className="loading-spinner"></div>
          <p className="page-loading-text">Lade Abo-Status...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="subscription-page">
      {/* Header */}
      <div className="subscription-header">
        <h1>Premium Abo</h1>
        <p>Wähle deinen Plan und starte durch!</p>
      </div>

      {/* Success message */}
      {isSuccess && (
        <div
          className="weight-alert info"
          style={{ marginBottom: 'var(--spacing-lg)' }}
        >
          <strong>Zahlung erfolgreich!</strong>
          <p>Dein Abo ist jetzt aktiv. Viel Erfolg bei deiner Diät!</p>
        </div>
      )}

      {/* Cancelled message */}
      {isCancelled && (
        <div
          className="weight-alert warning"
          style={{ marginBottom: 'var(--spacing-lg)' }}
        >
          <strong>Zahlung abgebrochen</strong>
          <p>Du kannst jederzeit erneut abonnieren.</p>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="auth-error" style={{ marginBottom: 'var(--spacing-lg)' }}>
          {error}
        </div>
      )}

      {/* Current subscription status */}
      {isActive && subscription && (
        <div className="subscription-status">
          <h2>Dein aktuelles Abo</h2>
          <div className="subscription-info">
            <div className="subscription-info-row">
              <span className="subscription-info-label">Status</span>
              <span
                className={`subscription-info-value ${
                  subscription.cancel_at_period_end
                    ? 'subscription-cancelled'
                    : 'subscription-active'
                }`}
              >
                {subscription.cancel_at_period_end ? 'Gekündigt' : 'Aktiv'}
              </span>
            </div>
            <div className="subscription-info-row">
              <span className="subscription-info-label">Plan</span>
              <span className="subscription-info-value">
                {subscription.plan === 'yearly' ? 'Jährlich' : 'Monatlich'}
              </span>
            </div>
            {subscription.current_period_end && (
              <div className="subscription-info-row">
                <span className="subscription-info-label">
                  {subscription.cancel_at_period_end
                    ? 'Läuft ab am'
                    : 'Nächste Zahlung'}
                </span>
                <span className="subscription-info-value">
                  {new Date(subscription.current_period_end).toLocaleDateString(
                    'de-DE'
                  )}
                </span>
              </div>
            )}
          </div>

          <div
            style={{
              display: 'flex',
              gap: 'var(--spacing-md)',
              marginTop: 'var(--spacing-lg)',
            }}
          >
            <button
              className="btn btn-secondary"
              onClick={handleManage}
              disabled={isProcessing}
            >
              Zahlungen verwalten
            </button>
            {subscription.cancel_at_period_end ? (
              <button
                className="btn btn-primary"
                onClick={handleReactivate}
                disabled={isProcessing}
              >
                Abo reaktivieren
              </button>
            ) : (
              <button
                className="btn btn-danger"
                onClick={handleCancel}
                disabled={isProcessing}
              >
                Abo kündigen
              </button>
            )}
          </div>
        </div>
      )}

      {/* Pricing cards - only show if not active */}
      {!isActive && (
        <>
          <div className="pricing-grid">
            {/* Monthly plan */}
            <div className="pricing-card">
              <h3 className="pricing-name">Monatlich</h3>
              <div className="pricing-price">
                <span className="pricing-amount">29,99€</span>
                <span className="pricing-period">/Monat</span>
              </div>
              <div className="pricing-features">
                <ul>
                  <li>Alle 100 Mahlzeitenpläne</li>
                  <li>Personalisierte Ernährung</li>
                  <li>Gewichtstracking</li>
                  <li>Fortschrittsanalyse</li>
                  <li>Jederzeit kündbar</li>
                </ul>
              </div>
              <div className="pricing-cta">
                <button
                  className="btn btn-primary btn-full btn-lg"
                  onClick={() => handleSubscribe('monthly')}
                  disabled={isProcessing}
                >
                  {isProcessing ? 'Laden...' : 'Jetzt starten'}
                </button>
              </div>
            </div>

            {/* Yearly plan - popular */}
            <div className="pricing-card popular">
              <span className="pricing-badge">Beliebt</span>
              <h3 className="pricing-name">Jährlich</h3>
              <div className="pricing-price">
                <span className="pricing-amount">239,99€</span>
                <span className="pricing-period">/Jahr</span>
                <div className="pricing-savings">2 Monate gratis!</div>
              </div>
              <div className="pricing-features">
                <ul>
                  <li>Alle 100 Mahlzeitenpläne</li>
                  <li>Personalisierte Ernährung</li>
                  <li>Gewichtstracking</li>
                  <li>Fortschrittsanalyse</li>
                  <li>Jederzeit kündbar</li>
                </ul>
              </div>
              <div className="pricing-cta">
                <button
                  className="btn btn-primary btn-full btn-lg"
                  onClick={() => handleSubscribe('yearly')}
                  disabled={isProcessing}
                >
                  {isProcessing ? 'Laden...' : 'Jetzt sparen'}
                </button>
              </div>
            </div>
          </div>

          {/* Promo code section */}
          <div className="promo-code-section">
            <h3 style={{ fontSize: '1rem', marginBottom: 'var(--spacing-md)' }}>
              Hast du einen Promo-Code?
            </h3>
            {promoValid ? (
              <div className="promo-applied">
                <span>✓</span>
                <span>{promoMessage}</span>
                <button
                  className="toast-close"
                  onClick={() => {
                    setPromoCode('');
                    setPromoValid(null);
                    setPromoMessage('');
                  }}
                >
                  ×
                </button>
              </div>
            ) : (
              <div className="promo-code-form">
                <input
                  type="text"
                  className="form-input"
                  placeholder="Promo-Code eingeben"
                  value={promoCode}
                  onChange={(e) => {
                    setPromoCode(e.target.value.toUpperCase());
                    setPromoValid(null);
                    setPromoMessage('');
                  }}
                />
                <button className="btn btn-secondary" onClick={validatePromo}>
                  Anwenden
                </button>
              </div>
            )}
            {promoValid === false && promoMessage && (
              <p
                style={{
                  color: 'var(--color-error)',
                  fontSize: '0.875rem',
                  marginTop: 'var(--spacing-sm)',
                }}
              >
                {promoMessage}
              </p>
            )}
          </div>
        </>
      )}

      {/* Back button */}
      <div style={{ marginTop: 'var(--spacing-xl)', textAlign: 'center' }}>
        <button
          className="btn btn-secondary"
          onClick={() => navigate('/profile')}
        >
          Zurück zum Profil
        </button>
      </div>
    </div>
  );
}
