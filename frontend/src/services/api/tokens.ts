/**
 * Token Management
 *
 * Handles localStorage operations for JWT tokens.
 * Isolated module makes it easy to switch to cookies or other storage.
 */

import { AUTH_CONFIG } from '@/config';

export const getAccessToken = (): string | null => {
  return localStorage.getItem(AUTH_CONFIG.tokenKey);
};

export const getRefreshToken = (): string | null => {
  return localStorage.getItem(AUTH_CONFIG.refreshKey);
};

export const setTokens = (accessToken: string, refreshToken: string): void => {
  localStorage.setItem(AUTH_CONFIG.tokenKey, accessToken);
  localStorage.setItem(AUTH_CONFIG.refreshKey, refreshToken);
};

export const clearTokens = (): void => {
  localStorage.removeItem(AUTH_CONFIG.tokenKey);
  localStorage.removeItem(AUTH_CONFIG.refreshKey);
};

export const hasValidToken = (): boolean => {
  return !!getAccessToken();
};
