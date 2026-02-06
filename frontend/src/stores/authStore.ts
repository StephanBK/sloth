/**
 * Auth Store - Global Authentication State
 *
 * Zustand store for managing authentication state.
 * Uses persist middleware to keep user logged in across sessions.
 *
 * TUTORIAL: https://docs.pmnd.rs/zustand/getting-started/introduction
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserProfile } from '@/types';
import { AUTH_CONFIG } from '@/config';
import { authApi, userApi, getAccessToken, clearTokens } from '@/services/api';

// =============================================================================
// Store Types
// =============================================================================

interface AuthState {
  // State
  user: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  handleOAuthCallback: () => Promise<boolean>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  updateUser: (user: UserProfile) => void;
  clearError: () => void;
  checkAuth: () => Promise<boolean>;
}

// =============================================================================
// Error Extraction Helper
// =============================================================================

function extractErrorMessage(err: unknown, fallback: string): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const axiosErr = err as { response?: { data?: { detail?: string }; status?: number } };
    return axiosErr.response?.data?.detail || `Error ${axiosErr.response?.status}`;
  }
  if (err instanceof Error) {
    return err.message;
  }
  return fallback;
}

// =============================================================================
// Auth Store
// =============================================================================

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,

      /**
       * Login with email and password
       */
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.login({ email, password });
          const user = await userApi.getProfile();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (err: unknown) {
          const message = extractErrorMessage(err, 'Login failed');
          set({ error: message, isLoading: false, isAuthenticated: false });
          throw err;
        }
      },

      /**
       * Register new user
       */
      register: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.register({ email, password });
          const user = await userApi.getProfile();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (err: unknown) {
          const message = extractErrorMessage(err, 'Registration failed');
          set({ error: message, isLoading: false, isAuthenticated: false });
          throw err;
        }
      },

      /**
       * Initiate Google OAuth login
       */
      loginWithGoogle: async () => {
        set({ isLoading: true, error: null });
        try {
          const url = await authApi.getGoogleOAuthUrl();
          window.location.href = url;
        } catch (err: unknown) {
          const message = extractErrorMessage(err, 'Google login failed');
          set({ error: message, isLoading: false });
          throw err;
        }
      },

      /**
       * Handle OAuth callback after Google redirects back
       */
      handleOAuthCallback: async () => {
        set({ isLoading: true, error: null });
        try {
          const tokens = await authApi.handleOAuthCallback();
          if (tokens) {
            const user = await userApi.getProfile();
            set({ user, isAuthenticated: true, isLoading: false });
            return true;
          } else {
            set({ error: 'OAuth callback failed - no tokens found', isLoading: false });
            return false;
          }
        } catch (err: unknown) {
          const message = extractErrorMessage(err, 'OAuth callback failed');
          set({ error: message, isLoading: false, isAuthenticated: false });
          return false;
        }
      },

      /**
       * Logout user
       */
      logout: async () => {
        set({ isLoading: true });
        try {
          await authApi.logout();
        } finally {
          clearTokens();
          set({ user: null, isAuthenticated: false, isLoading: false, error: null });
        }
      },

      /**
       * Fetch current user profile (restore session on app startup)
       */
      fetchUser: async () => {
        const token = getAccessToken();
        if (!token) {
          set({ user: null, isAuthenticated: false });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await userApi.getProfile();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          clearTokens();
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },

      /**
       * Update user in store (after profile changes)
       */
      updateUser: (user: UserProfile) => {
        set({ user });
      },

      /**
       * Clear error message
       */
      clearError: () => {
        set({ error: null });
      },

      /**
       * Check if user is authenticated
       */
      checkAuth: async () => {
        const { isAuthenticated, user } = get();

        if (isAuthenticated && user) {
          return true;
        }

        const token = getAccessToken();
        if (token) {
          try {
            const fetchedUser = await userApi.getProfile();
            set({ user: fetchedUser, isAuthenticated: true });
            return true;
          } catch {
            clearTokens();
            set({ user: null, isAuthenticated: false });
            return false;
          }
        }

        return false;
      },
    }),
    {
      name: AUTH_CONFIG.storageKey,
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// =============================================================================
// Selector Hooks
// =============================================================================

/**
 * Check if user needs to complete intake form
 */
export const useNeedsIntake = () => {
  const user = useAuthStore((state) => state.user);
  return user ? !user.intake_completed : false;
};

/**
 * Get current user's diet level
 */
export const useCurrentLevel = () => {
  const user = useAuthStore((state) => state.user);
  return user?.current_level ?? 1;
};

/**
 * Get current user's gender
 */
export const useUserGender = () => {
  const user = useAuthStore((state) => state.user);
  return user?.gender;
};
