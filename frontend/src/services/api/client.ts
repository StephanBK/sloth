/**
 * API Client - Axios instance with interceptors
 *
 * This module provides a configured Axios instance that:
 * - Automatically adds auth tokens to requests
 * - Handles token refresh on 401 errors
 * - Redirects to login when auth fails
 */

import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { API_CONFIG, ROUTES } from '@/config';
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from './tokens';
import type { TokenRefreshResponse } from '@/types';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_CONFIG.baseUrl,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // If 401 and we have a refresh token, try to refresh
    if (error.response?.status === 401 && originalRequest) {
      const refreshToken = getRefreshToken();

      if (refreshToken) {
        try {
          // Use a new axios instance to avoid interceptor loop
          const response = await axios.post<TokenRefreshResponse>(
            `${API_CONFIG.baseUrl}/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const { access_token, refresh_token: new_refresh_token } = response.data;
          setTokens(access_token, new_refresh_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } catch {
          // Refresh failed - clear tokens and redirect
          clearTokens();
          window.location.href = ROUTES.login;
        }
      } else {
        // No refresh token - redirect to login
        clearTokens();
        window.location.href = ROUTES.login;
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
