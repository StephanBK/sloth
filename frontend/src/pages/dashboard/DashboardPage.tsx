/**
 * Dashboard Page - Main app screen after login
 *
 * LEARNING NOTE:
 * This is the main screen users see after completing intake.
 * For MVP, we show:
 * - Welcome message with user info
 * - Current diet level
 * - Weight progress summary
 * - Logout button
 *
 * This will expand to include meal plans, weight tracking, etc.
 *
 * TUTORIAL: https://tanstack.com/query/latest/docs/react/guides/queries
 */

import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, logout, isLoading } = useAuthStore();

  if (!user) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="dashboard-page">
      {/* Header */}
      <div className="dashboard-header">
        <h1 className="dashboard-title">
          Hallo{user.email ? `, ${user.email.split('@')[0]}` : ''}!
        </h1>
        <button
          className="btn btn-secondary"
          onClick={handleLogout}
          disabled={isLoading}
        >
          Abmelden
        </button>
      </div>

      {/* Dashboard content */}
      <div className="dashboard-content">
        {/* Current level card */}
        <div className="card">
          <h2 style={{ marginBottom: '0.5rem' }}>Dein aktuelles Level</h2>
          <div
            style={{
              fontSize: '3rem',
              fontWeight: 'bold',
              color: 'var(--color-primary)',
            }}
          >
            Level {user.current_level}
          </div>
          <p className="text-muted" style={{ marginTop: '0.5rem' }}>
            {getLevelDescription(user.current_level)}
          </p>
        </div>

        {/* Weight progress card */}
        {user.starting_weight_kg && user.goal_weight_kg && (
          <div className="card">
            <h2 style={{ marginBottom: '1rem' }}>Gewichtsfortschritt</h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', textAlign: 'center' }}>
              <div>
                <div style={{ fontSize: '0.875rem', color: 'var(--color-gray-500)' }}>Start</div>
                <div style={{ fontSize: '1.5rem', fontWeight: '600' }}>
                  {user.starting_weight_kg.toFixed(1)} kg
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: 'var(--color-gray-500)' }}>Aktuell</div>
                <div style={{ fontSize: '1.5rem', fontWeight: '600', color: 'var(--color-primary)' }}>
                  {user.current_weight_kg?.toFixed(1) || '—'} kg
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: 'var(--color-gray-500)' }}>Ziel</div>
                <div style={{ fontSize: '1.5rem', fontWeight: '600' }}>
                  {user.goal_weight_kg.toFixed(1)} kg
                </div>
              </div>
            </div>

            {/* Progress bar */}
            {user.total_weight_lost !== null && user.weight_to_lose !== null && (
              <div style={{ marginTop: '1.5rem' }}>
                <div
                  style={{
                    height: '0.5rem',
                    backgroundColor: 'var(--color-gray-200)',
                    borderRadius: 'var(--radius-full)',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      backgroundColor: 'var(--color-success)',
                      borderRadius: 'var(--radius-full)',
                      width: `${Math.min(100, Math.max(0, getProgressPercent(user)))}%`,
                      transition: 'width 0.3s ease',
                    }}
                  />
                </div>
                <p className="text-muted text-center" style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                  {user.total_weight_lost > 0
                    ? `${user.total_weight_lost.toFixed(1)} kg abgenommen!`
                    : 'Deine Reise beginnt jetzt!'}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Quick actions */}
        <div className="card">
          <h2 style={{ marginBottom: '1rem' }}>Schnellaktionen</h2>
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            <button
              className="btn btn-primary btn-full"
              onClick={() => navigate('/weight')}
            >
              Gewicht eintragen
            </button>
            <button className="btn btn-secondary btn-full" disabled>
              Mahlzeiten ansehen (kommt bald)
            </button>
            <button className="btn btn-secondary btn-full" disabled>
              Einkaufsliste (kommt bald)
            </button>
          </div>
        </div>

        {/* Profile info (debug) */}
        <div className="card" style={{ backgroundColor: 'var(--color-gray-50)' }}>
          <h3 style={{ marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--color-gray-500)' }}>
            Dein Profil
          </h3>
          <div style={{ fontSize: '0.875rem', color: 'var(--color-gray-600)' }}>
            <p>Geschlecht: {user.gender === 'male' ? 'Männlich' : 'Weiblich'}</p>
            <p>Größe: {user.height_cm} cm</p>
            <p>Alter: {user.age} Jahre</p>
            <p>Aktivität: {getActivityLabel(user.activity_level)}</p>
            {user.bmi && <p>BMI: {user.bmi.toFixed(1)}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Helper Functions
// =============================================================================

function getLevelDescription(level: number): string {
  const descriptions: Record<number, string> = {
    1: 'Sanfter Einstieg - Hohe Kalorienzufuhr',
    2: 'Leichtes Defizit - Gut für den Anfang',
    3: 'Moderates Defizit - Stetige Fortschritte',
    4: 'Stärkeres Defizit - Für Fortgeschrittene',
    5: 'Intensiv - Nur für erfahrene Nutzer',
  };
  return descriptions[level] || 'Dein personalisierter Ernährungsplan';
}

function getActivityLabel(level: string | null): string {
  const labels: Record<string, string> = {
    sedentary: 'Sitzend',
    light: 'Leicht aktiv',
    moderate: 'Moderat aktiv',
    active: 'Sehr aktiv',
  };
  return level ? labels[level] || level : '—';
}

function getProgressPercent(user: { starting_weight_kg?: number | null; current_weight_kg?: number | null; goal_weight_kg?: number | null }): number {
  if (!user.starting_weight_kg || !user.current_weight_kg || !user.goal_weight_kg) {
    return 0;
  }
  const totalToLose = user.starting_weight_kg - user.goal_weight_kg;
  if (totalToLose <= 0) return 100;
  const lost = user.starting_weight_kg - user.current_weight_kg;
  return (lost / totalToLose) * 100;
}
