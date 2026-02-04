"""
Stripe Payment Service

Handles all Stripe-related operations:
- Creating checkout sessions
- Managing subscriptions
- Processing webhooks
- Customer portal access

TUTORIAL: https://stripe.com/docs/billing/subscriptions/overview
"""

import stripe
from functools import lru_cache
from typing import Optional
from datetime import datetime

from app.config import get_settings
from app.schemas.subscription import (
    SubscriptionPlan,
    SubscriptionStatus,
    SubscriptionResponse,
)


class StripeService:
    """Service for Stripe payment operations"""

    def __init__(self):
        settings = get_settings()
        self.secret_key = settings.stripe_secret_key
        self.publishable_key = settings.stripe_publishable_key
        self.webhook_secret = settings.stripe_webhook_secret
        self.price_monthly = settings.stripe_price_monthly
        self.price_yearly = settings.stripe_price_yearly
        self.frontend_url = settings.frontend_url

        # Configure Stripe
        if self.secret_key:
            stripe.api_key = self.secret_key

    def is_configured(self) -> bool:
        """Check if Stripe is properly configured"""
        return bool(self.secret_key and self.price_monthly)

    def get_price_id(self, plan: SubscriptionPlan) -> str:
        """Get Stripe price ID for a subscription plan"""
        if plan == SubscriptionPlan.MONTHLY:
            return self.price_monthly
        elif plan == SubscriptionPlan.YEARLY:
            return self.price_yearly
        else:
            raise ValueError(f"Unknown plan: {plan}")

    async def create_checkout_session(
        self,
        user_id: str,
        user_email: str,
        plan: SubscriptionPlan,
        promo_code: Optional[str] = None,
    ) -> dict:
        """
        Create a Stripe Checkout session for subscription.

        Returns the checkout URL and session ID.
        """
        if not self.is_configured():
            raise ValueError("Stripe not configured. Add API keys to .env")

        price_id = self.get_price_id(plan)

        # Build checkout session parameters
        session_params = {
            "mode": "subscription",
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            "success_url": f"{self.frontend_url}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{self.frontend_url}/subscription/cancelled",
            "client_reference_id": user_id,
            "customer_email": user_email,
            "metadata": {
                "user_id": user_id,
                "plan": plan.value,
            },
            # Allow promotion codes
            "allow_promotion_codes": True,
        }

        # If specific promo code provided, apply it
        if promo_code:
            try:
                # Look up the promotion code
                promo_codes = stripe.PromotionCode.list(code=promo_code, active=True)
                if promo_codes.data:
                    session_params["discounts"] = [
                        {"promotion_code": promo_codes.data[0].id}
                    ]
                    # Remove allow_promotion_codes when discount is applied
                    del session_params["allow_promotion_codes"]
            except stripe.error.StripeError:
                pass  # Ignore invalid promo codes, let user enter at checkout

        # Create checkout session
        session = stripe.checkout.Session.create(**session_params)

        return {
            "checkout_url": session.url,
            "session_id": session.id,
        }

    async def get_or_create_customer(
        self,
        user_id: str,
        email: str,
        stripe_customer_id: Optional[str] = None,
    ) -> str:
        """Get existing or create new Stripe customer"""
        if stripe_customer_id:
            return stripe_customer_id

        # Create new customer
        customer = stripe.Customer.create(
            email=email,
            metadata={"user_id": user_id},
        )
        return customer.id

    async def get_subscription_status(
        self,
        stripe_customer_id: Optional[str],
    ) -> SubscriptionResponse:
        """Get the current subscription status for a customer"""
        if not stripe_customer_id:
            return SubscriptionResponse(status=SubscriptionStatus.NONE)

        try:
            # Get active subscriptions for customer
            subscriptions = stripe.Subscription.list(
                customer=stripe_customer_id,
                status="all",
                limit=1,
            )

            if not subscriptions.data:
                return SubscriptionResponse(
                    status=SubscriptionStatus.NONE,
                    stripe_customer_id=stripe_customer_id,
                )

            sub = subscriptions.data[0]

            # Map Stripe status to our status
            status_map = {
                "active": SubscriptionStatus.ACTIVE,
                "canceled": SubscriptionStatus.CANCELLED,
                "past_due": SubscriptionStatus.PAST_DUE,
                "trialing": SubscriptionStatus.TRIALING,
                "incomplete": SubscriptionStatus.INCOMPLETE,
            }
            status = status_map.get(sub.status, SubscriptionStatus.NONE)

            # Determine plan from price ID
            price_id = sub["items"]["data"][0]["price"]["id"]
            if price_id == self.price_monthly:
                plan = SubscriptionPlan.MONTHLY
            elif price_id == self.price_yearly:
                plan = SubscriptionPlan.YEARLY
            else:
                plan = None

            return SubscriptionResponse(
                status=status,
                plan=plan,
                current_period_end=datetime.fromtimestamp(sub.current_period_end),
                cancel_at_period_end=sub.cancel_at_period_end,
                stripe_customer_id=stripe_customer_id,
            )

        except stripe.error.StripeError as e:
            # Log error and return no subscription
            print(f"Stripe error getting subscription: {e}")
            return SubscriptionResponse(
                status=SubscriptionStatus.NONE,
                stripe_customer_id=stripe_customer_id,
            )

    async def cancel_subscription(
        self,
        stripe_customer_id: str,
        cancel_at_period_end: bool = True,
    ) -> bool:
        """Cancel a customer's subscription"""
        try:
            subscriptions = stripe.Subscription.list(
                customer=stripe_customer_id,
                status="active",
                limit=1,
            )

            if not subscriptions.data:
                return False

            sub = subscriptions.data[0]

            if cancel_at_period_end:
                # Cancel at end of billing period
                stripe.Subscription.modify(
                    sub.id,
                    cancel_at_period_end=True,
                )
            else:
                # Cancel immediately
                stripe.Subscription.delete(sub.id)

            return True

        except stripe.error.StripeError as e:
            print(f"Stripe error cancelling subscription: {e}")
            return False

    async def reactivate_subscription(
        self,
        stripe_customer_id: str,
    ) -> bool:
        """Reactivate a cancelled subscription (before period ends)"""
        try:
            subscriptions = stripe.Subscription.list(
                customer=stripe_customer_id,
                limit=1,
            )

            if not subscriptions.data:
                return False

            sub = subscriptions.data[0]

            if sub.cancel_at_period_end:
                stripe.Subscription.modify(
                    sub.id,
                    cancel_at_period_end=False,
                )
                return True

            return False

        except stripe.error.StripeError:
            return False

    async def create_customer_portal_session(
        self,
        stripe_customer_id: str,
    ) -> str:
        """Create a Stripe Customer Portal session for self-service"""
        if not stripe_customer_id:
            raise ValueError("No Stripe customer ID provided")

        session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=f"{self.frontend_url}/profile",
        )

        return session.url

    async def validate_promo_code(self, code: str) -> dict:
        """Validate a promotion code and return discount info"""
        try:
            promo_codes = stripe.PromotionCode.list(code=code, active=True, limit=1)

            if not promo_codes.data:
                return {
                    "valid": False,
                    "message": "Ungültiger Promo-Code",
                }

            promo = promo_codes.data[0]
            coupon = promo.coupon

            # Get discount details
            if coupon.percent_off:
                return {
                    "valid": True,
                    "discount_percent": int(coupon.percent_off),
                    "message": f"{int(coupon.percent_off)}% Rabatt wird angewendet",
                }
            elif coupon.amount_off:
                amount = coupon.amount_off / 100  # Convert from cents
                return {
                    "valid": True,
                    "discount_amount": amount,
                    "message": f"{amount:.2f}€ Rabatt wird angewendet",
                }
            else:
                return {
                    "valid": True,
                    "message": "Promo-Code gültig",
                }

        except stripe.error.StripeError:
            return {
                "valid": False,
                "message": "Fehler bei der Validierung",
            }

    def construct_webhook_event(
        self,
        payload: bytes,
        sig_header: str,
    ):
        """Construct and verify a Stripe webhook event"""
        if not self.webhook_secret:
            raise ValueError("Webhook secret not configured")

        return stripe.Webhook.construct_event(
            payload,
            sig_header,
            self.webhook_secret,
        )


@lru_cache()
def get_stripe_service() -> StripeService:
    """Get cached StripeService instance"""
    return StripeService()
