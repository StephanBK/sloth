/**
 * Grocery List Page
 *
 * Generates a shopping list from a selected range of meal plan days.
 * Aggregates ingredients by name and lets users check off items.
 */

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { mealPlanApi } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';
import type { MealPlan, Gender } from '@/types';

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

interface AggregatedItem {
  name: string;
  quantities: { amount: number; unit: string }[];
  displayAmount: string;
  checked: boolean;
}

export default function GroceryListPage() {
  const user = useAuthStore((state) => state.user);
  const userLevel = user?.current_level ?? 1;
  const userGender = user?.gender ?? 'male';

  const [selectedDays, setSelectedDays] = useState<number[]>([1, 2, 3]);
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());

  // Fetch meal plans for user's level and gender
  const { data: mealPlans, isLoading: isLoadingList } = useQuery<MealPlanListItem[]>({
    queryKey: ['meal-plans', userLevel, userGender],
    queryFn: () => mealPlanApi.list({ level: userLevel, gender: userGender }),
  });

  // Fetch details for selected meal plans
  const selectedPlanIds = mealPlans
    ?.filter(p => selectedDays.includes(p.day_number))
    ?.map(p => p.id) || [];

  const mealPlanQueries = useQuery<MealPlan[]>({
    queryKey: ['meal-plans-details', selectedPlanIds],
    queryFn: async () => {
      const plans = await Promise.all(
        selectedPlanIds.map(id => mealPlanApi.get(id))
      );
      return plans;
    },
    enabled: selectedPlanIds.length > 0,
  });

  const detailedPlans = mealPlanQueries.data || [];

  // Aggregate ingredients
  const groceryItems = useMemo(() => {
    const itemMap = new Map<string, { amounts: Map<string, number> }>();

    detailedPlans.forEach(plan => {
      plan.meals.forEach(meal => {
        meal.ingredients.forEach(ingredient => {
          const name = ingredient.product_name.trim().toLowerCase();

          if (!itemMap.has(name)) {
            itemMap.set(name, { amounts: new Map() });
          }

          const item = itemMap.get(name)!;
          const unit = ingredient.unit.toLowerCase();
          const current = item.amounts.get(unit) || 0;
          item.amounts.set(unit, current + ingredient.quantity);
        });
      });
    });

    const items: AggregatedItem[] = [];
    itemMap.forEach((value, key) => {
      const quantities: { amount: number; unit: string }[] = [];
      const displayParts: string[] = [];

      value.amounts.forEach((amount, unit) => {
        const rounded = Math.round(amount * 10) / 10;
        quantities.push({ amount: rounded, unit });
        displayParts.push(`${rounded} ${unit}`);
      });

      // Capitalize first letter
      const displayName = key.charAt(0).toUpperCase() + key.slice(1);

      items.push({
        name: displayName,
        quantities,
        displayAmount: displayParts.join(' + '),
        checked: checkedItems.has(key),
      });
    });

    // Sort: unchecked first, then alphabetically
    items.sort((a, b) => {
      if (a.checked !== b.checked) return a.checked ? 1 : -1;
      return a.name.localeCompare(b.name, 'de');
    });

    return items;
  }, [detailedPlans, checkedItems]);

  const toggleItem = (name: string) => {
    const key = name.toLowerCase();
    setCheckedItems(prev => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const toggleDay = (day: number) => {
    setSelectedDays(prev =>
      prev.includes(day)
        ? prev.filter(d => d !== day)
        : [...prev, day].sort((a, b) => a - b)
    );
    setCheckedItems(new Set()); // Reset checks when changing days
  };

  const checkedCount = groceryItems.filter(i => i.checked).length;
  const totalCount = groceryItems.length;

  const handleClearAll = () => setCheckedItems(new Set());

  return (
    <div className="grocery-page">
      {/* Header */}
      <div className="grocery-header">
        <h1>Einkaufsliste</h1>
        {totalCount > 0 && (
          <span className="grocery-count">{checkedCount}/{totalCount}</span>
        )}
      </div>

      {/* Day selector */}
      <div className="grocery-day-selector">
        <p className="grocery-day-label">Tage auswählen:</p>
        <div className="grocery-days">
          {Array.from({ length: 10 }, (_, i) => i + 1).map(day => (
            <button
              key={day}
              className={`grocery-day-btn ${selectedDays.includes(day) ? 'active' : ''}`}
              onClick={() => toggleDay(day)}
            >
              {day}
            </button>
          ))}
        </div>
        <div className="grocery-day-presets">
          <button
            className="grocery-preset-btn"
            onClick={() => { setSelectedDays([1, 2, 3]); setCheckedItems(new Set()); }}
          >
            Tag 1-3
          </button>
          <button
            className="grocery-preset-btn"
            onClick={() => { setSelectedDays([1, 2, 3, 4, 5]); setCheckedItems(new Set()); }}
          >
            Tag 1-5
          </button>
          <button
            className="grocery-preset-btn"
            onClick={() => { setSelectedDays(Array.from({ length: 10 }, (_, i) => i + 1)); setCheckedItems(new Set()); }}
          >
            Alle
          </button>
        </div>
      </div>

      {/* Loading */}
      {(isLoadingList || mealPlanQueries.isLoading) && (
        <div className="grocery-loading">
          <div className="loading-spinner"></div>
          <p>Einkaufsliste wird erstellt...</p>
        </div>
      )}

      {/* Grocery list */}
      {!isLoadingList && !mealPlanQueries.isLoading && groceryItems.length > 0 && (
        <>
          {checkedCount > 0 && (
            <div className="grocery-progress">
              <div className="grocery-progress-bar">
                <div
                  className="grocery-progress-fill"
                  style={{ width: `${(checkedCount / totalCount) * 100}%` }}
                />
              </div>
              <button className="grocery-clear-btn" onClick={handleClearAll}>
                Zurücksetzen
              </button>
            </div>
          )}

          <div className="grocery-list">
            {groceryItems.map((item) => (
              <div
                key={item.name}
                className={`grocery-item ${item.checked ? 'checked' : ''}`}
                onClick={() => toggleItem(item.name)}
              >
                <div className={`grocery-checkbox ${item.checked ? 'checked' : ''}`}>
                  {item.checked && (
                    <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  )}
                </div>
                <div className="grocery-item-text">
                  <span className="grocery-item-name">{item.name}</span>
                  <span className="grocery-item-amount">{item.displayAmount}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="grocery-summary">
            <strong>{totalCount}</strong> Zutaten für <strong>{selectedDays.length}</strong> Tag{selectedDays.length !== 1 ? 'e' : ''}
          </div>
        </>
      )}

      {/* Empty state */}
      {!isLoadingList && !mealPlanQueries.isLoading && selectedDays.length === 0 && (
        <div className="grocery-empty">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--color-gray-300)" strokeWidth="1.5" width="64" height="64">
            <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <path d="M16 10a4 4 0 0 1-8 0" />
          </svg>
          <h2>Wähle Tage aus</h2>
          <p>Tippe oben auf die Tage, für die du einkaufen möchtest.</p>
        </div>
      )}
    </div>
  );
}
