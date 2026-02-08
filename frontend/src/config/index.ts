/**
 * Application Configuration
 *
 * Centralizes all environment variables and app configuration.
 * This makes it easy to change settings in one place.
 */

// API Configuration
export const API_CONFIG = {
  baseUrl: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000, // 30 seconds
} as const;

// Auth Configuration
export const AUTH_CONFIG = {
  tokenKey: 'sloth_access_token',
  refreshKey: 'sloth_refresh_token',
  storageKey: 'sloth-auth-storage',
} as const;

// Query Configuration (React Query)
export const QUERY_CONFIG = {
  staleTime: 1000 * 60 * 5, // 5 minutes
  retry: 1,
} as const;

// Subscription Configuration
export const SUBSCRIPTION_CONFIG = {
  monthlyPrice: 29.99,
  yearlyPrice: 239.99,
  currency: 'EUR',
} as const;

// App Routes
export const ROUTES = {
  // Public
  login: '/login',
  register: '/register',
  authCallback: '/auth/callback',

  // Protected
  dashboard: '/dashboard',
  intake: '/intake',
  weight: '/weight',
  meals: '/meals',
  grocery: '/grocery',
  profile: '/profile',
  subscription: '/subscription',
  subscriptionSuccess: '/subscription/success',
  subscriptionCancelled: '/subscription/cancelled',
} as const;
