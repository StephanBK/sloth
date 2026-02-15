/**
 * API Module - Central Export
 *
 * This file re-exports all API modules for convenient importing.
 * Import like: import { authApi, userApi } from '@/services/api';
 *
 * Structure:
 * - client.ts: Axios instance with interceptors
 * - tokens.ts: JWT token management
 * - auth.ts: Authentication API calls
 * - user.ts: User profile API calls
 * - weight.ts: Weight tracking API calls
 * - mealPlan.ts: Meal plan API calls
 * - subscription.ts: Stripe subscription API calls
 */

// Re-export all API modules
export { authApi } from './auth';
export { userApi } from './user';
export { weightApi } from './weight';
export { mealPlanApi, type MealPlanListItem, type MealPlanFilters } from './mealPlan';
export {
  productsApi,
  type Product,
  type ProductListItem,
  type ProductFilters,
  type ProductStats,
} from './products';
export {
  subscriptionApi,
  type SubscriptionPlan,
  type SubscriptionStatus,
  type SubscriptionInfo,
  type CheckoutResponse,
  type PromoCodeResponse,
} from './subscription';

// Re-export token utilities for stores
export {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
  hasValidToken,
} from './tokens';

// Re-export the client for advanced use cases
export { apiClient as api } from './client';

// Legacy default export for backward compatibility
export default {
  auth: { authApi: 'use named import instead' },
  user: { userApi: 'use named import instead' },
  weight: { weightApi: 'use named import instead' },
  mealPlan: { mealPlanApi: 'use named import instead' },
  subscription: { subscriptionApi: 'use named import instead' },
};
