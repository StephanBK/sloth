/**
 * Custom Hooks Index
 *
 * Re-exports all custom hooks.
 * Import like: import { useWeightHistory, useIsMobile } from '@/hooks';
 */

// API hooks
export {
  queryKeys,
  useWeightHistory,
  useCreateWeightEntry,
  useUpdateWeightEntry,
  useDeleteWeightEntry,
  useMealPlans,
  useMealPlan,
  useSubscription,
  useCreateCheckout,
  useCancelSubscription,
  useReactivateSubscription,
  useValidatePromoCode,
  useUpdateProfile,
} from './useApi';

// Utility hooks
export { useLocalStorage } from './useLocalStorage';
export { useMediaQuery, useIsMobile, useIsTablet, useIsDesktop } from './useMediaQuery';
