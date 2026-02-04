"""
Subscription/Payment API Router

Handles:
- Creating checkout sessions
- Getting subscription status
- Cancelling subscriptions
- Stripe webhook processing
- Promo code validation
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Header, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.stripe_service import StripeService, get_stripe_service
from app.schemas.subscription import (
    CreateCheckoutRequest,
    CancelSubscriptionRequest,
    ApplyPromoCodeRequest,
    CheckoutSessionResponse,
    SubscriptionResponse,
    PromoCodeResponse,
    CustomerPortalResponse,
    WebhookResponse,
    SubscriptionStatus,
)

import stripe
from datetime import datetime

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)


@router.post(
    "/checkout",
    response_model=CheckoutSessionResponse,
    summary="Create checkout session",
)
async def create_checkout(
    request: CreateCheckoutRequest,
    current_user: User = Depends(get_current_user),
    stripe_service: StripeService = Depends(get_stripe_service),
):
    """
    Create a Stripe Checkout session to start subscription.

    Returns a URL to redirect the user to for payment.
    """
    if not stripe_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system not configured",
        )

    try:
        result = await stripe_service.create_checkout_session(
            user_id=current_user.id,
            user_email=current_user.email,
            plan=request.plan,
            promo_code=request.promo_code,
        )
        return CheckoutSessionResponse(
            checkout_url=result["checkout_url"],
            session_id=result["session_id"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}",
        )


@router.get(
    "/status",
    response_model=SubscriptionResponse,
    summary="Get subscription status",
)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    stripe_service: StripeService = Depends(get_stripe_service),
):
    """Get the current user's subscription status"""
    if not stripe_service.is_configured():
        return SubscriptionResponse(status=SubscriptionStatus.NONE)

    return await stripe_service.get_subscription_status(
        current_user.stripe_customer_id
    )


@router.post(
    "/cancel",
    response_model=SubscriptionResponse,
    summary="Cancel subscription",
)
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    stripe_service: StripeService = Depends(get_stripe_service),
    db: Session = Depends(get_db),
):
    """
    Cancel the current subscription.

    By default, cancels at the end of the billing period.
    Set cancel_at_period_end=False to cancel immediately.
    """
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found",
        )

    success = await stripe_service.cancel_subscription(
        current_user.stripe_customer_id,
        request.cancel_at_period_end,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel subscription",
        )

    # Update local status
    current_user.subscription_status = "cancelled"
    db.commit()

    return await stripe_service.get_subscription_status(
        current_user.stripe_customer_id
    )


@router.post(
    "/reactivate",
    response_model=SubscriptionResponse,
    summary="Reactivate cancelled subscription",
)
async def reactivate_subscription(
    current_user: User = Depends(get_current_user),
    stripe_service: StripeService = Depends(get_stripe_service),
    db: Session = Depends(get_db),
):
    """
    Reactivate a subscription that was cancelled but hasn't expired yet.
    """
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No subscription to reactivate",
        )

    success = await stripe_service.reactivate_subscription(
        current_user.stripe_customer_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reactivate subscription",
        )

    # Update local status
    current_user.subscription_status = "active"
    db.commit()

    return await stripe_service.get_subscription_status(
        current_user.stripe_customer_id
    )


@router.post(
    "/portal",
    response_model=CustomerPortalResponse,
    summary="Get customer portal URL",
)
async def get_customer_portal(
    current_user: User = Depends(get_current_user),
    stripe_service: StripeService = Depends(get_stripe_service),
):
    """
    Get a URL to the Stripe Customer Portal.

    Users can manage their subscription, payment methods,
    and view invoices through the portal.
    """
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer account found",
        )

    try:
        url = await stripe_service.create_customer_portal_session(
            current_user.stripe_customer_id
        )
        return CustomerPortalResponse(portal_url=url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create portal session: {str(e)}",
        )


@router.post(
    "/validate-promo",
    response_model=PromoCodeResponse,
    summary="Validate promo code",
)
async def validate_promo_code(
    request: ApplyPromoCodeRequest,
    stripe_service: StripeService = Depends(get_stripe_service),
):
    """Validate a promotion code before checkout"""
    if not stripe_service.is_configured():
        return PromoCodeResponse(
            valid=False,
            message="Payment system not configured",
        )

    result = await stripe_service.validate_promo_code(request.promo_code)
    return PromoCodeResponse(**result)


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    summary="Stripe webhook endpoint",
)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="stripe-signature"),
    stripe_service: StripeService = Depends(get_stripe_service),
    db: Session = Depends(get_db),
):
    """
    Handle Stripe webhook events.

    This endpoint receives events from Stripe when:
    - Checkout is completed
    - Subscription is created/updated/cancelled
    - Payment succeeds/fails

    IMPORTANT: This endpoint must be publicly accessible.
    Stripe verifies authenticity via the signature header.
    """
    # Get raw request body
    payload = await request.body()

    try:
        event = stripe_service.construct_webhook_event(
            payload,
            stripe_signature,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    # Handle different event types
    event_type = event["type"]
    data = event["data"]["object"]

    try:
        if event_type == "checkout.session.completed":
            # User completed checkout
            await handle_checkout_completed(data, db)

        elif event_type == "customer.subscription.created":
            # New subscription created
            await handle_subscription_created(data, db)

        elif event_type == "customer.subscription.updated":
            # Subscription updated (status change, plan change, etc.)
            await handle_subscription_updated(data, db)

        elif event_type == "customer.subscription.deleted":
            # Subscription cancelled/expired
            await handle_subscription_deleted(data, db)

        elif event_type == "invoice.payment_failed":
            # Payment failed
            await handle_payment_failed(data, db)

    except Exception as e:
        # Log error but return 200 to acknowledge receipt
        print(f"Webhook handler error: {e}")

    return WebhookResponse(received=True)


# =============================================================================
# Webhook Event Handlers
# =============================================================================

async def handle_checkout_completed(data: dict, db: Session):
    """Handle successful checkout completion"""
    user_id = data.get("client_reference_id")
    customer_id = data.get("customer")

    if not user_id:
        return

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.stripe_customer_id = customer_id
        user.subscription_status = "active"
        db.commit()


async def handle_subscription_created(data: dict, db: Session):
    """Handle new subscription creation"""
    customer_id = data.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.subscription_status = data.get("status", "active")
        if data.get("current_period_end"):
            user.subscription_ends_at = datetime.fromtimestamp(
                data["current_period_end"]
            )
        db.commit()


async def handle_subscription_updated(data: dict, db: Session):
    """Handle subscription updates"""
    customer_id = data.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.subscription_status = data.get("status", user.subscription_status)
        if data.get("current_period_end"):
            user.subscription_ends_at = datetime.fromtimestamp(
                data["current_period_end"]
            )
        db.commit()


async def handle_subscription_deleted(data: dict, db: Session):
    """Handle subscription cancellation/deletion"""
    customer_id = data.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.subscription_status = "cancelled"
        user.subscription_ends_at = None
        db.commit()


async def handle_payment_failed(data: dict, db: Session):
    """Handle failed payment"""
    customer_id = data.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.subscription_status = "past_due"
        db.commit()
