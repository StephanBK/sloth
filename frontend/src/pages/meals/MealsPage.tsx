/**
 * Meals Page - Browse meal plans by level and day
 *
 * LEARNING NOTE:
 * This page shows meal plans filtered by the user's gender and current level.
 * Users can browse through their weekly meal plans and see details for each day.
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { mealPlanApi } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';
import type { MealPlan, Gender } from '@/types';
import { getLevelLabel } from '@/types';

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

export default function MealsPage() {
  const user = useAuthStore((state) => state.user);
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);

  // User's current level and gender
  const userLevel = user?.current_level ?? 1;
  const userGender = user?.gender ?? 'male';

  // Fetch meal plans for user's level and gender
  const { data: mealPlans, isLoading, error } = useQuery<MealPlanListItem[]>({
    queryKey: ['meal-plans', userLevel, userGender],
    queryFn: () => mealPlanApi.list({ level: userLevel, gender: userGender }),
  });

  // Fetch selected meal plan details
  const { data: selectedPlan, isLoading: isLoadingPlan } = useQuery<MealPlan>({
    queryKey: ['meal-plan', selectedPlanId],
    queryFn: () => mealPlanApi.get(selectedPlanId!),
    enabled: !!selectedPlanId,
  });

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="meals-page">
        <div className="card">
          <p style={{ color: 'var(--color-error)' }}>
            Fehler beim Laden der Mahlzeiten. Bitte versuche es erneut.
          </p>
        </div>
      </div>
    );
  }

  const dayNames = [
    'Tag 1', 'Tag 2', 'Tag 3', 'Tag 4', 'Tag 5',
    'Tag 6', 'Tag 7', 'Tag 8', 'Tag 9', 'Tag 10'
  ];

  return (
    <div className="meals-page">
      {/* Header */}
      <div className="meals-header">
        <h1>Deine Mahlzeiten</h1>
        <div className="meals-level-badge">
          {getLevelLabel(userLevel, userGender)}
        </div>
      </div>

      {/* Level info */}
      <div className="meals-info-card">
        <p>
          Dein aktuelles Kalorienlevel: <strong>{getLevelLabel(userLevel, userGender)}</strong>.
          Hier findest du deine täglichen Mahlzeitenpläne.
        </p>
      </div>

      {/* Meal plans grid */}
      {mealPlans && mealPlans.length > 0 ? (
        <div className="meals-grid">
          {mealPlans.map((plan) => (
            <div
              key={plan.id}
              className="meal-plan-card"
              onClick={() => setSelectedPlanId(plan.id)}
            >
              <div className="meal-plan-day">
                {dayNames[plan.day_number - 1] || `Tag ${plan.day_number}`}
              </div>
              <div className="meal-plan-name">
                {plan.name || 'Mahlzeitenplan'}
              </div>
              <div className="meal-plan-macros">
                <span className="macro">
                  <strong>{plan.total_kcal}</strong> kcal
                </span>
                <span className="macro">
                  <strong>{plan.total_protein}g</strong> Protein
                </span>
              </div>
              <div className="meal-plan-macros-secondary">
                <span>{plan.total_carbs}g Kohlenhydrate</span>
                <span>{plan.total_fat}g Fett</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="meals-empty">
          <div className="meals-empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M3 3h18v18H3zM12 8v4m0 4h.01" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h2>Keine Mahlzeitenpläne verfügbar</h2>
          <p>Für dein aktuelles Kalorienlevel sind noch keine Pläne hinterlegt.</p>
        </div>
      )}

      {/* Meal Plan Detail Modal */}
      {selectedPlanId && (
        <MealPlanModal
          plan={selectedPlan}
          isLoading={isLoadingPlan}
          onClose={() => setSelectedPlanId(null)}
        />
      )}
    </div>
  );
}

// =============================================================================
// Meal Plan Detail Modal
// =============================================================================

interface MealPlanModalProps {
  plan: MealPlan | undefined;
  isLoading: boolean;
  onClose: () => void;
}

function MealPlanModal({ plan, isLoading, onClose }: MealPlanModalProps) {
  const mealTypeLabels: Record<string, string> = {
    breakfast: 'Frühstück',
    lunch: 'Mittagessen',
    dinner: 'Abendessen',
    snack: 'Snack',
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content meal-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{plan?.name || 'Mahlzeitenplan'}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        {isLoading ? (
          <div className="modal-loading">
            <div className="loading-spinner"></div>
          </div>
        ) : plan ? (
          <div className="meal-modal-content">
            {/* Daily summary */}
            <div className="meal-summary">
              <div className="meal-summary-item">
                <span className="meal-summary-value">{plan.total_kcal}</span>
                <span className="meal-summary-label">kcal</span>
              </div>
              <div className="meal-summary-item">
                <span className="meal-summary-value">{Math.round(plan.total_protein)}g</span>
                <span className="meal-summary-label">Protein</span>
              </div>
              <div className="meal-summary-item">
                <span className="meal-summary-value">{Math.round(plan.total_carbs)}g</span>
                <span className="meal-summary-label">Kohlenhydrate</span>
              </div>
              <div className="meal-summary-item">
                <span className="meal-summary-value">{Math.round(plan.total_fat)}g</span>
                <span className="meal-summary-label">Fett</span>
              </div>
            </div>

            {/* Meals */}
            <div className="meals-list">
              {plan.meals
                .sort((a, b) => {
                  const order = ['breakfast', 'lunch', 'snack', 'dinner'];
                  return order.indexOf(a.meal_type) - order.indexOf(b.meal_type);
                })
                .map((meal) => (
                  <div key={meal.id} className="meal-item">
                    <div className="meal-item-header">
                      <span className="meal-type-badge">
                        {mealTypeLabels[meal.meal_type] || meal.meal_type}
                      </span>
                      <span className="meal-kcal">{meal.total_kcal} kcal</span>
                    </div>

                    {meal.instructions && (
                      <p className="meal-instructions">{meal.instructions}</p>
                    )}

                    <div className="ingredients-list">
                      {meal.ingredients
                        .sort((a, b) => a.order_index - b.order_index)
                        .map((ingredient) => (
                          <div key={ingredient.id} className="ingredient-item">
                            <span className="ingredient-name">{ingredient.product_name}</span>
                            <span className="ingredient-amount">
                              {ingredient.quantity} {ingredient.unit}
                            </span>
                            <span className="ingredient-kcal">{ingredient.kcal} kcal</span>
                          </div>
                        ))}
                    </div>

                    <div className="meal-macros">
                      <span>P: {Math.round(meal.total_protein)}g</span>
                      <span>K: {Math.round(meal.total_carbs)}g</span>
                      <span>F: {Math.round(meal.total_fat)}g</span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ) : (
          <div className="modal-error">
            <p>Mahlzeitenplan konnte nicht geladen werden.</p>
          </div>
        )}
      </div>
    </div>
  );
}
