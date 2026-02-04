"""
Subscription Schemas

Pydantic models for payment/subscription requests and responses.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class SubscriptionPlan(str, Enum):
    """Available subscription plans"""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatus(str, Enum):
    """Subscription status values"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    NONE = "none"


# =============================================================================
# Request Schemas
# =============================================================================

class CreateCheckoutRequest(BaseModel):
    """Request to create a Stripe checkout session"""
    plan: SubscriptionPlan
    promo_code: Optional[str] = None


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel subscription"""
    cancel_at_period_end: bool = True  # Cancel at end of billing period


class ApplyPromoCodeRequest(BaseModel):
    """Request to validate/apply a promo code"""
    promo_code: str


# =============================================================================
# Response Schemas
# =============================================================================

class CheckoutSessionResponse(BaseModel):
    """Response with Stripe checkout URL"""
    checkout_url: str
    session_id: str


class SubscriptionResponse(BaseModel):
    """Current subscription status"""
    status: SubscriptionStatus
    plan: Optional[SubscriptionPlan] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    stripe_customer_id: Optional[str] = None


class PromoCodeResponse(BaseModel):
    """Promo code validation response"""
    valid: bool
    discount_percent: Optional[int] = None
    discount_amount: Optional[float] = None
    message: str


class CustomerPortalResponse(BaseModel):
    """Stripe Customer Portal URL"""
    portal_url: str


class WebhookResponse(BaseModel):
    """Webhook processing response"""
    received: bool
    message: str = "Webhook processed"
