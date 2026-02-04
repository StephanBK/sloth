/**
 * Subscription API Module
 *
 * Handles all Stripe subscription-related API calls.
 */

import apiClient from './client';

// Subscription types
export type SubscriptionPlan = 'monthly' | 'yearly';

export type SubscriptionStatus =
  | 'active'
  | 'cancelled'
  | 'past_due'
  | 'trialing'
  | 'incomplete'
  | 'none';

export interface SubscriptionInfo {
  status: SubscriptionStatus;
  plan?: SubscriptionPlan;
  current_period_end?: string;
  cancel_at_period_end: boolean;
  stripe_customer_id?: string;
}

export interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
}

export interface PromoCodeResponse {
  valid: boolean;
  discount_percent?: number;
  discount_amount?: number;
  message: string;
}

interface CustomerPortalResponse {
  portal_url: string;
}

export const subscriptionApi = {
  /**
   * Get current subscription status
   */
  getStatus: async (): Promise<SubscriptionInfo> => {
    const response = await apiClient.get<SubscriptionInfo>('/subscriptions/status');
    return response.data;
  },

  /**
   * Create checkout session for subscription
   */
  createCheckout: async (
    plan: SubscriptionPlan,
    promoCode?: string
  ): Promise<CheckoutResponse> => {
    const response = await apiClient.post<CheckoutResponse>('/subscriptions/checkout', {
      plan,
      promo_code: promoCode,
    });
    return response.data;
  },

  /**
   * Cancel current subscription
   */
  cancel: async (cancelAtPeriodEnd: boolean = true): Promise<SubscriptionInfo> => {
    const response = await apiClient.post<SubscriptionInfo>('/subscriptions/cancel', {
      cancel_at_period_end: cancelAtPeriodEnd,
    });
    return response.data;
  },

  /**
   * Reactivate cancelled subscription
   */
  reactivate: async (): Promise<SubscriptionInfo> => {
    const response = await apiClient.post<SubscriptionInfo>('/subscriptions/reactivate');
    return response.data;
  },

  /**
   * Get customer portal URL for self-service
   */
  getPortalUrl: async (): Promise<string> => {
    const response = await apiClient.post<CustomerPortalResponse>('/subscriptions/portal');
    return response.data.portal_url;
  },

  /**
   * Validate promo code
   */
  validatePromoCode: async (code: string): Promise<PromoCodeResponse> => {
    const response = await apiClient.post<PromoCodeResponse>('/subscriptions/validate-promo', {
      promo_code: code,
    });
    return response.data;
  },
};
