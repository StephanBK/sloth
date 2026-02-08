/**
 * Dashboard Page - Beautiful, sleek main screen
 *
 * Shows:
 * - Greeting with time of day
 * - Today's meal plan card (rotates based on day of year)
 * - Weight progress with mini trend
 * - Quick weight entry
 * - Quick action cards
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/authStore';
import { mealPlanApi, weightApi } from '@/services/api';
import type { MealPlan, Gender, WeightHistory } from '@/types';

interface MealPlanListItem {
  id: string;
  level: number;
  day_number: number;
  gender: Gender;
  total_kcal: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  name: string | null;
  created_at: string;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [showWeightModal, setShowWeightModal] = useState(false);
  const [quickWeight, setQuickWeight] = useState('');
  const [weightSaving, setWeightSaving] = useState(false);
  const [weightSaved, setWeightSaved] = useState(false);

  const userLevel = user?.current_level ?? 1;
  const userGender = user?.gender ?? 'male';

  // Today's day number (1-10, rotating)
  const dayOfYear = Math.floor(
    (Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000
  );
  const todayDayNumber = ((dayOfYear - 1) % 10) + 1;

  // Fetch meal plans
  const { data: mealPlans } = useQuery<MealPlanListItem[]>({
    queryKey: ['meal-plans', userLevel, userGender],
    queryFn: () => mealPlanApi.list({ level: userLevel, gender: userGender }),
  });

  // Fetch today's meal plan detail
  const todayPlan = mealPlans?.find(p => p.day_number === todayDayNumber);
  const { data: todayMealPlan } = useQuery<MealPlan>({
    queryKey: ['meal-plan', todayPlan?.id],
    queryFn: () => mealPlanApi.get(todayPlan!.id),
    enabled: !!todayPlan?.id,
  });

  // Fetch weight history (prefetch for cache, used by weight page)
  useQuery<WeightHistory>({
    queryKey: ['weight', 7],
    queryFn: () => weightApi.getHistory(7),
  });

  if (!user) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  const greeting = getGreeting();
  const firstName = user.email ? user.email.split('@')[0] : '';
  const progressPercent = getProgressPercent(user);

  const handleQuickWeight = async () => {
    const weight = parseFloat(quickWeight);
    if (isNaN(weight) || weight < 30 || weight > 300) return;

    setWeightSaving(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      await weightApi.createEntry({ weight_kg: weight, measured_at: today });
      setWeightSaved(true);
      setQuickWeight('');
      setTimeout(() => {
        setShowWeightModal(false);
        setWeightSaved(false);
      }, 1500);
    } catch {
      // silently fail
    } finally {
      setWeightSaving(false);
    }
  };

  const mealTypeLabels: Record<string, string> = {
    breakfast: 'Frühstück',
    lunch: 'Mittagessen',
    dinner: 'Abendessen',
    snack: 'Snack',
  };

  const mealTypeEmojis: Record<string, string> = {
    breakfast: '🌅',
    lunch: '☀️',
    snack: '🍎',
    dinner: '🌙',
  };

  // Get the current/next meal based on time
  const currentHour = new Date().getHours();
  const currentMealType = currentHour < 10 ? 'breakfast' : currentHour < 14 ? 'lunch' : currentHour < 17 ? 'snack' : 'dinner';

  return (
    <div className="dashboard-page">
      {/* Hero Header */}
      <div className="dash-hero">
        <div className="dash-hero-text">
          <p className="dash-greeting">{greeting}</p>
          <h1 className="dash-name">{firstName}</h1>
        </div>
        <div className="dash-level-pill">
          <span className="dash-level-number">{userLevel}</span>
          <span className="dash-level-label">Stufe</span>
        </div>
      </div>

      {/* Weight Progress Card */}
      {user.starting_weight_kg && user.goal_weight_kg && (
        <div className="dash-progress-card" onClick={() => navigate('/weight')}>
          <div className="dash-progress-header">
            <h2>Fortschritt</h2>
            <span className="dash-progress-percent">
              {Math.round(Math.max(0, progressPercent))}%
            </span>
          </div>
          <div className="dash-progress-bar-container">
            <div className="dash-progress-bar">
              <div
                className="dash-progress-fill"
                style={{ width: `${Math.min(100, Math.max(0, progressPercent))}%` }}
              />
            </div>
          </div>
          <div className="dash-weight-row">
            <div className="dash-weight-item">
              <span className="dash-weight-value">{user.starting_weight_kg.toFixed(1)}</span>
              <span className="dash-weight-label">Start</span>
            </div>
            <div className="dash-weight-item current">
              <span className="dash-weight-value">
                {user.current_weight_kg?.toFixed(1) || '—'}
              </span>
              <span className="dash-weight-label">Aktuell</span>
            </div>
            <div className="dash-weight-item">
              <span className="dash-weight-value">{user.goal_weight_kg.toFixed(1)}</span>
              <span className="dash-weight-label">Ziel</span>
            </div>
          </div>
          {user.total_weight_lost !== null && user.total_weight_lost > 0 && (
            <div className="dash-weight-lost">
              {user.total_weight_lost.toFixed(1)} kg verloren
            </div>
          )}
        </div>
      )}

      {/* Quick Weight Entry */}
      <div className="dash-quick-weight" onClick={() => setShowWeightModal(true)}>
        <div className="dash-quick-weight-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="16" />
            <line x1="8" y1="12" x2="16" y2="12" />
          </svg>
        </div>
        <div className="dash-quick-weight-text">
          <strong>Gewicht eintragen</strong>
          <span>Schnell dein heutiges Gewicht loggen</span>
        </div>
        <svg className="dash-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </div>

      {/* Today's Meals Card */}
      {todayMealPlan && (
        <div className="dash-meals-card">
          <div className="dash-meals-header">
            <div>
              <h2>Heute - Tag {todayDayNumber}</h2>
              <p className="dash-meals-kcal">{todayMealPlan.total_kcal} kcal</p>
            </div>
            <button
              className="dash-meals-all-btn"
              onClick={() => navigate('/meals')}
            >
              Alle Tage
            </button>
          </div>

          <div className="dash-meals-macros">
            <div className="dash-macro">
              <div className="dash-macro-bar" style={{ '--macro-color': '#4F7942', '--macro-pct': `${Math.min(100, (todayMealPlan.total_protein / (todayMealPlan.total_protein + todayMealPlan.total_carbs + todayMealPlan.total_fat)) * 100)}%` } as React.CSSProperties} />
              <span>{Math.round(todayMealPlan.total_protein)}g</span>
              <label>Protein</label>
            </div>
            <div className="dash-macro">
              <div className="dash-macro-bar" style={{ '--macro-color': '#f59e0b', '--macro-pct': `${Math.min(100, (todayMealPlan.total_carbs / (todayMealPlan.total_protein + todayMealPlan.total_carbs + todayMealPlan.total_fat)) * 100)}%` } as React.CSSProperties} />
              <span>{Math.round(todayMealPlan.total_carbs)}g</span>
              <label>Kohlenhydrate</label>
            </div>
            <div className="dash-macro">
              <div className="dash-macro-bar" style={{ '--macro-color': '#ef4444', '--macro-pct': `${Math.min(100, (todayMealPlan.total_fat / (todayMealPlan.total_protein + todayMealPlan.total_carbs + todayMealPlan.total_fat)) * 100)}%` } as React.CSSProperties} />
              <span>{Math.round(todayMealPlan.total_fat)}g</span>
              <label>Fett</label>
            </div>
          </div>

          <div className="dash-meals-list">
            {todayMealPlan.meals
              .sort((a, b) => {
                const order = ['breakfast', 'lunch', 'snack', 'dinner'];
                return order.indexOf(a.meal_type) - order.indexOf(b.meal_type);
              })
              .map((meal) => (
                <div
                  key={meal.id}
                  className={`dash-meal-item ${meal.meal_type === currentMealType ? 'active' : ''}`}
                >
                  <span className="dash-meal-emoji">{mealTypeEmojis[meal.meal_type] || '🍽️'}</span>
                  <div className="dash-meal-info">
                    <strong>{mealTypeLabels[meal.meal_type]}</strong>
                    <span>{meal.total_kcal} kcal</span>
                  </div>
                  <div className="dash-meal-detail">
                    {meal.ingredients.slice(0, 2).map(i => i.product_name).join(', ')}
                    {meal.ingredients.length > 2 && ` +${meal.ingredients.length - 2}`}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Quick Actions Grid */}
      <div className="dash-actions">
        <div className="dash-action-card" onClick={() => navigate('/meals')}>
          <div className="dash-action-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 8h1a4 4 0 0 1 0 8h-1" />
              <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z" />
              <line x1="6" y1="1" x2="6" y2="4" />
              <line x1="10" y1="1" x2="10" y2="4" />
              <line x1="14" y1="1" x2="14" y2="4" />
            </svg>
          </div>
          <span>Mahlzeiten</span>
        </div>
        <div className="dash-action-card" onClick={() => navigate('/weight')}>
          <div className="dash-action-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <span>Gewicht</span>
        </div>
        <div className="dash-action-card" onClick={() => navigate('/grocery')}>
          <div className="dash-action-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <path d="M16 10a4 4 0 0 1-8 0" />
            </svg>
          </div>
          <span>Einkaufsliste</span>
        </div>
        <div className="dash-action-card" onClick={() => navigate('/profile')}>
          <div className="dash-action-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <span>Profil</span>
        </div>
      </div>

      {/* Quick Weight Modal */}
      {showWeightModal && (
        <div className="modal-overlay" onClick={() => !weightSaving && setShowWeightModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Gewicht eintragen</h2>
              <button className="modal-close" onClick={() => setShowWeightModal(false)}>×</button>
            </div>
            <div style={{ padding: 'var(--spacing-lg)' }}>
              {weightSaved ? (
                <div className="dash-weight-success">
                  <svg viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" strokeWidth="2" width="48" height="48">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                    <polyline points="22 4 12 14.01 9 11.01" />
                  </svg>
                  <p>Gespeichert!</p>
                </div>
              ) : (
                <>
                  <div className="form-group">
                    <label className="form-label">Gewicht (kg)</label>
                    <input
                      type="number"
                      className="form-input"
                      placeholder="z.B. 78.5"
                      value={quickWeight}
                      onChange={(e) => setQuickWeight(e.target.value)}
                      step="0.1"
                      min="30"
                      max="300"
                      autoFocus
                    />
                  </div>
                  <button
                    className="btn btn-primary btn-full btn-lg"
                    onClick={handleQuickWeight}
                    disabled={weightSaving || !quickWeight}
                  >
                    {weightSaving ? 'Speichern...' : 'Speichern'}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Helper Functions
// =============================================================================

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Guten Morgen';
  if (hour < 18) return 'Guten Tag';
  return 'Guten Abend';
}

function getProgressPercent(user: {
  starting_weight_kg?: number | null;
  current_weight_kg?: number | null;
  goal_weight_kg?: number | null;
}): number {
  if (!user.starting_weight_kg || !user.current_weight_kg || !user.goal_weight_kg) return 0;
  const totalToLose = user.starting_weight_kg - user.goal_weight_kg;
  if (totalToLose <= 0) return 100;
  const lost = user.starting_weight_kg - user.current_weight_kg;
  return (lost / totalToLose) * 100;
}
