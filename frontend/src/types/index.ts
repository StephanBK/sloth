/**
 * TypeScript Types for Sloth Frontend
 *
 * LEARNING NOTE:
 * These types match the Pydantic schemas from our backend.
 * TypeScript helps catch errors at compile time instead of runtime.
 *
 * TUTORIAL: https://www.typescriptlang.org/docs/handbook/2/everyday-types.html
 */

// =============================================================================
// Enums (match backend)
// =============================================================================

export type Gender = 'male' | 'female';

export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active';

// =============================================================================
// Auth Types
// =============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface AuthUser {
  id: string;
  email: string;
  email_confirmed: boolean | null;
}

export interface AuthSession {
  access_token: string;
  refresh_token: string;
  expires_at: number | null;
}

export interface AuthResponse {
  user: AuthUser;
  session: AuthSession | null;
  message: string | null;
}

export interface TokenRefreshResponse {
  access_token: string;
  refresh_token: string;
  expires_at: number | null;
}

// =============================================================================
// User Profile Types
// =============================================================================

export interface UserProfile {
  id: string;
  email: string;
  gender: Gender | null;
  height_cm: number | null;
  age: number | null;
  current_weight_kg: number | null;
  goal_weight_kg: number | null;
  starting_weight_kg: number | null;
  activity_level: ActivityLevel | null;
  dietary_restrictions: string[] | null;
  current_level: number;
  intake_completed: boolean;
  profile_picture_url: string | null;
  bmi: number | null;
  weight_to_lose: number | null;
  total_weight_lost: number | null;
  created_at: string;
  updated_at: string;
}

// Intake form screens
export interface IntakeScreen1 {
  gender: Gender;
  height_cm: number;
  age: number;
}

export interface IntakeScreen2 {
  current_weight_kg: number;
  goal_weight_kg: number;
}

export interface IntakeScreen3 {
  activity_level: ActivityLevel;
  dietary_restrictions?: string[];
}

export interface IntakeComplete extends IntakeScreen1, IntakeScreen2, IntakeScreen3 {}

export interface ProfileUpdate {
  gender?: Gender;
  height_cm?: number;
  age?: number;
  current_weight_kg?: number;
  goal_weight_kg?: number;
  activity_level?: ActivityLevel;
  dietary_restrictions?: string[];
  current_level?: number;
}

// =============================================================================
// Weight Tracking Types
// =============================================================================

export interface WeightEntry {
  id: string;
  weight_kg: number;
  measured_at: string; // ISO date string (YYYY-MM-DD)
  notes: string | null;
  created_at: string;
}

export interface WeightEntryCreate {
  weight_kg: number;
  measured_at: string;
  notes?: string;
}

export interface WeightEntryUpdate {
  weight_kg?: number;
  measured_at?: string;
  notes?: string;
}

export interface WeightHistoryPoint {
  date: string;
  weight_kg: number;
  is_interpolated: boolean;
}

export interface WeightStats {
  starting_weight_kg: number | null;
  current_weight_kg: number | null;
  goal_weight_kg: number | null;
  total_lost_kg: number | null;
  remaining_kg: number | null;
  progress_percent: number | null;
}

export interface StallStatus {
  can_detect: boolean;
  is_stalled: boolean;
  entries_in_period: number;
  min_entries_needed: number;
  weight_change_kg: number | null;
  message: string;
}

export interface WeightHistory {
  history: WeightHistoryPoint[];
  stats: WeightStats;
  stall_status: StallStatus;
  entries: WeightEntry[];
}

// =============================================================================
// Meal Plan Types
// =============================================================================

export interface Ingredient {
  id: string;
  product_name: string;
  quantity: number;
  unit: string;
  kcal: number;
  protein: number;
  carbs: number;
  fat: number;
  order_index: number;
}

export interface Meal {
  id: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  order_index: number;
  instructions: string | null;
  total_kcal: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  ingredients: Ingredient[];
}

export interface MealPlan {
  id: string;
  level: number;
  day_number: number;
  gender: Gender;
  total_kcal: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  name: string | null;
  description: string | null;
  meals: Meal[];
  created_at: string;
  updated_at: string;
}

// =============================================================================
// Product Types
// =============================================================================

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

// =============================================================================
// API Response Types
// =============================================================================

export interface ApiError {
  detail: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}
