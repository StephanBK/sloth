/**
 * User API Module
 *
 * Handles user profile and intake-related API calls.
 */

import apiClient from './client';
import type {
  UserProfile,
  IntakeComplete,
  IntakeScreen1,
  IntakeScreen2,
  IntakeScreen3,
  ProfileUpdate,
} from '@/types';

export const userApi = {
  /**
   * Get current user's profile
   */
  getProfile: async (): Promise<UserProfile> => {
    const response = await apiClient.get<UserProfile>('/users/me');
    return response.data;
  },

  /**
   * Complete intake form (all at once)
   */
  completeIntake: async (data: IntakeComplete): Promise<UserProfile> => {
    const response = await apiClient.post<UserProfile>('/users/me/intake', data);
    return response.data;
  },

  /**
   * Save intake screen 1 (partial)
   */
  saveIntakeScreen1: async (data: IntakeScreen1): Promise<void> => {
    await apiClient.post('/users/me/intake/screen1', data);
  },

  /**
   * Save intake screen 2 (partial)
   */
  saveIntakeScreen2: async (data: IntakeScreen2): Promise<void> => {
    await apiClient.post('/users/me/intake/screen2', data);
  },

  /**
   * Save intake screen 3 and complete intake
   */
  saveIntakeScreen3: async (data: IntakeScreen3): Promise<UserProfile> => {
    const response = await apiClient.post<UserProfile>('/users/me/intake/screen3', data);
    return response.data;
  },

  /**
   * Update user profile (partial update)
   */
  updateProfile: async (data: ProfileUpdate): Promise<UserProfile> => {
    const response = await apiClient.patch<UserProfile>('/users/me', data);
    return response.data;
  },
};
