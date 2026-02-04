/**
 * Weight Tracking API Module
 *
 * Handles all weight-related API calls.
 */

import apiClient from './client';
import type { WeightHistory, WeightEntry, WeightEntryCreate, WeightEntryUpdate } from '@/types';

export const weightApi = {
  /**
   * Get weight history with stats and stall detection
   */
  getHistory: async (days: number = 30): Promise<WeightHistory> => {
    const response = await apiClient.get<WeightHistory>('/weight', {
      params: { days },
    });
    return response.data;
  },

  /**
   * Log a new weight entry
   */
  createEntry: async (data: WeightEntryCreate): Promise<WeightEntry> => {
    const response = await apiClient.post<WeightEntry>('/weight', data);
    return response.data;
  },

  /**
   * Get a single weight entry
   */
  getEntry: async (id: string): Promise<WeightEntry> => {
    const response = await apiClient.get<WeightEntry>(`/weight/${id}`);
    return response.data;
  },

  /**
   * Update a weight entry
   */
  updateEntry: async (id: string, data: WeightEntryUpdate): Promise<WeightEntry> => {
    const response = await apiClient.patch<WeightEntry>(`/weight/${id}`, data);
    return response.data;
  },

  /**
   * Delete a weight entry
   */
  deleteEntry: async (id: string): Promise<void> => {
    await apiClient.delete(`/weight/${id}`);
  },
};
