/**
 * Products API Module
 *
 * Handles all product catalog API calls.
 */

import apiClient from './client';

// Types specific to product API
export interface Product {
  id: string;
  name: string;
  brand: string | null;
  ean: string | null;
  category: string;
  package_size: number | null;
  unit: string | null;
  calories_per_100g: number | null;
  protein_per_100g: number | null;
  carbs_per_100g: number | null;
  fat_per_100g: number | null;
  fiber_per_100g: number | null;
  sugar_per_100g: number | null;
  salt_per_100g: number | null;
  data_source: string;
  is_curated: boolean;
  data_confidence: number | null;
  nutriscore_grade: string | null;
  image_url: string | null;
  image_thumb_url: string | null;
  off_id: string | null;
  bls_code: string | null;
  last_synced_at: string | null;
  notes: string | null;
}

export interface ProductListItem {
  id: string;
  name: string;
  brand: string | null;
  category: string;
  package_size: number | null;
  unit: string | null;
  data_source: string;
  is_curated: boolean;
  nutriscore_grade: string | null;
  image_thumb_url: string | null;
}

export interface ProductFilters {
  category?: string;
  search?: string;
  data_source?: string;
  curated_only?: boolean;
  min_confidence?: number;
  has_nutrition?: boolean;
  skip?: number;
  limit?: number;
}

export interface ProductStats {
  total: number;
  by_source: Record<string, number>;
  curated: number;
  with_nutrition: number;
}

export const productsApi = {
  /**
   * List products with optional filters
   */
  list: async (filters?: ProductFilters): Promise<ProductListItem[]> => {
    const response = await apiClient.get<ProductListItem[]>('/products', {
      params: filters,
    });
    return response.data;
  },

  /**
   * Get a single product with full details and availability
   */
  get: async (id: string): Promise<Product> => {
    const response = await apiClient.get<Product>(`/products/${id}`);
    return response.data;
  },

  /**
   * Search products by name/brand with confidence ordering
   */
  search: async (q: string, limit: number = 20): Promise<ProductListItem[]> => {
    const response = await apiClient.get<ProductListItem[]>('/products/search', {
      params: { q, limit },
    });
    return response.data;
  },

  /**
   * List all product categories
   */
  categories: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/products/categories');
    return response.data;
  },

  /**
   * Get pipeline statistics
   */
  stats: async (): Promise<ProductStats> => {
    const response = await apiClient.get<ProductStats>('/products/stats');
    return response.data;
  },
};
