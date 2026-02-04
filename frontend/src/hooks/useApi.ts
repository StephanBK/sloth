/**
 * API Hooks
 *
 * React Query hooks for data fetching with loading/error states.
 * Provides consistent data fetching patterns across the app.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  weightApi,
  mealPlanApi,
  subscriptionApi,
  userApi,
  type MealPlanFilters,
  type SubscriptionPlan,
} from '@/services/api';
import type { WeightEntryCreate, WeightEntryUpdate, ProfileUpdate } from '@/types';

// =============================================================================
// Query Keys - Centralized for easy invalidation
// =============================================================================

export const queryKeys = {
  user: ['user'] as const,
  weight: (days?: number) => ['weight', days] as const,
  mealPlans: (filters?: MealPlanFilters) => ['mealPlans', filters] as const,
  mealPlan: (id: string) => ['mealPlan', id] as const,
  subscription: ['subscription'] as const,
};

// =============================================================================
// Weight Hooks
// =============================================================================

export function useWeightHistory(days: number = 30) {
  return useQuery({
    queryKey: queryKeys.weight(days),
    queryFn: () => weightApi.getHistory(days),
  });
}

export function useCreateWeightEntry() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: WeightEntryCreate) => weightApi.createEntry(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['weight'] });
    },
  });
}

export function useUpdateWeightEntry() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: WeightEntryUpdate }) =>
      weightApi.updateEntry(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['weight'] });
    },
  });
}

export function useDeleteWeightEntry() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => weightApi.deleteEntry(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['weight'] });
    },
  });
}

// =============================================================================
// Meal Plan Hooks
// =============================================================================

export function useMealPlans(filters?: MealPlanFilters) {
  return useQuery({
    queryKey: queryKeys.mealPlans(filters),
    queryFn: () => mealPlanApi.list(filters),
  });
}

export function useMealPlan(id: string) {
  return useQuery({
    queryKey: queryKeys.mealPlan(id),
    queryFn: () => mealPlanApi.get(id),
    enabled: !!id,
  });
}

// =============================================================================
// Subscription Hooks
// =============================================================================

export function useSubscription() {
  return useQuery({
    queryKey: queryKeys.subscription,
    queryFn: () => subscriptionApi.getStatus(),
  });
}

export function useCreateCheckout() {
  return useMutation({
    mutationFn: ({ plan, promoCode }: { plan: SubscriptionPlan; promoCode?: string }) =>
      subscriptionApi.createCheckout(plan, promoCode),
  });
}

export function useCancelSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (cancelAtPeriodEnd: boolean = true) => subscriptionApi.cancel(cancelAtPeriodEnd),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.subscription });
    },
  });
}

export function useReactivateSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => subscriptionApi.reactivate(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.subscription });
    },
  });
}

export function useValidatePromoCode() {
  return useMutation({
    mutationFn: (code: string) => subscriptionApi.validatePromoCode(code),
  });
}

// =============================================================================
// User Hooks
// =============================================================================

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ProfileUpdate) => userApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.user });
    },
  });
}
