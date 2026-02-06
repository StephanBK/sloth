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
   * Handle OAuth callback - exchange code for tokens
   * After Google OAuth, Supabase redirects with a code parameter
   */
  handleOAuthCallback: async (): Promise<{ accessToken: string; refreshToken: string } | null> => {
    // First check for tokens in URL hash (implicit flow)
    const hash = window.location.hash;
    if (hash) {
      const hashParams = new URLSearchParams(hash.substring(1));
      const accessToken = hashParams.get('access_token');
      const refreshToken = hashParams.get('refresh_token');

      if (accessToken && refreshToken) {
        setTokens(accessToken, refreshToken);
        return { accessToken, refreshToken };
      }
    }

    // Check for authorization code in URL params (code flow)
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
      try {
        const response = await apiClient.post<AuthResponse>('/auth/callback', { code });
        if (response.data.session) {
          setTokens(response.data.session.access_token, response.data.session.refresh_token);
          return {
            accessToken: response.data.session.access_token,
            refreshToken: response.data.session.refresh_token,
          };
        }
      } catch (error) {
        console.error('Failed to exchange code for tokens:', error);
        return null;
      }
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
