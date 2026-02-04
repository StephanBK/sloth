/**
 * Meal Plans API Module
 *
 * Handles all meal plan-related API calls.
 */

import apiClient from './client';
import type { MealPlan, Gender } from '@/types';

// Types specific to meal plan API
export interface MealPlanListItem {
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

export interface MealPlanFilters {
  level?: number;
  gender?: Gender;
  skip?: number;
  limit?: number;
}

export const mealPlanApi = {
  /**
   * List meal plans with optional filters
   */
  list: async (filters?: MealPlanFilters): Promise<MealPlanListItem[]> => {
    const response = await apiClient.get<MealPlanListItem[]>('/meal-plans', {
      params: filters,
    });
    return response.data;
  },

  /**
   * Get a single meal plan with full details (meals + ingredients)
   */
  get: async (id: string): Promise<MealPlan> => {
    const response = await apiClient.get<MealPlan>(`/meal-plans/${id}`);
    return response.data;
  },
};
