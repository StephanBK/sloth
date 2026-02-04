/**
 * Auth API Module
 *
 * Handles all authentication-related API calls.
 * Separated for maintainability and testing.
 */

import apiClient from './client';
import { setTokens } from './tokens';
import type { AuthResponse, LoginRequest, RegisterRequest } from '@/types';

export const authApi = {
  /**
   * Register a new user with email and password
   */
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    if (response.data.session) {
      setTokens(response.data.session.access_token, response.data.session.refresh_token);
    }
    return response.data;
  },

  /**
   * Login with email and password
   */
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', data);
    if (response.data.session) {
      setTokens(response.data.session.access_token, response.data.session.refresh_token);
    }
    return response.data;
  },

  /**
   * Get Google OAuth URL for redirect
   */
  getGoogleOAuthUrl: async (): Promise<string> => {
    const redirectUrl = `${window.location.origin}/auth/callback`;
    const response = await apiClient.post<{ url: string }>('/auth/google', {
      redirect_url: redirectUrl,
    });
    return response.data.url;
  },

  /**
   * Handle OAuth callback - extract tokens from URL hash
   * Supabase returns tokens in the URL fragment after Google auth
   */
  handleOAuthCallback: (): { accessToken: string; refreshToken: string } | null => {
    const hash = window.location.hash;
    if (!hash) return null;

    const params = new URLSearchParams(hash.substring(1));
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');

    if (accessToken && refreshToken) {
      setTokens(accessToken, refreshToken);
      return { accessToken, refreshToken };
    }
    return null;
  },

  /**
   * Logout - clears tokens locally
   */
  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout');
    } catch {
      // Ignore errors - we'll clear tokens anyway
    }
  },

  /**
   * Request password reset email
   */
  resetPassword: async (email: string): Promise<void> => {
    await apiClient.post('/auth/reset-password', { email });
  },
};
