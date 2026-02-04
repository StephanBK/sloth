"""
FastAPI Dependencies - Reusable request dependencies

LEARNING NOTE:
Dependencies are functions that run before your route handlers.
They can:
- Extract and validate data (like auth tokens)
- Connect to databases
- Check permissions
- Inject services

When you add `user = Depends(get_current_user)` to a route,
FastAPI automatically runs get_current_user and passes the result.

TUTORIAL: https://fastapi.tiangolo.com/tutorial/dependencies/
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.auth_service import AuthService, get_auth_service
from app.models.user import User, Gender

# HTTPBearer extracts the token from "Authorization: Bearer <token>" header
# LEARNING NOTE: This creates the "Authorize" button in /docs
security = HTTPBearer(
    scheme_name="Bearer Token",
    description="Enter your Supabase access token",
    auto_error=False,  # Don't auto-raise error, we'll handle it
)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get the current user if authenticated, or None if not.

    LEARNING NOTE:
    Use this for endpoints that work both authenticated and not,
    but show different content based on auth status.

    Example: A meal plan list that shows "liked" status only for logged-in users.
    """
    if not credentials:
        return None

    if not auth_service.is_configured():
        return None

    # Verify the JWT token
    token_data = auth_service.verify_token(credentials.credentials)
    if not token_data:
        return None

    # Get or create user in our database
    user = db.query(User).filter(User.id == token_data["user_id"]).first()

    return user


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current authenticated user. Raises 401 if not authenticated.

    LEARNING NOTE:
    Use this for endpoints that REQUIRE authentication.
    If the token is missing or invalid, FastAPI returns 401 Unauthorized.

    Usage in routes:
        @router.get("/profile")
        async def get_profile(user: User = Depends(get_current_user)):
            return {"email": user.email}
    """
    # Check if credentials provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if auth service is configured
    if not auth_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured",
        )

    # Verify the JWT token
    token_data = auth_service.verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from our database
    user = db.query(User).filter(User.id == token_data["user_id"]).first()

    if not user:
        # User exists in Supabase but not in our DB yet
        # This happens on first login - we need to create the user
        # For now, we'll create a minimal user record
        # The frontend should call a "complete profile" endpoint to add gender
        user = User(
            id=token_data["user_id"],
            email=token_data["email"],
            gender=Gender.MALE,  # Default, user should update this
            current_level=1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


async def get_current_user_id(
    user: User = Depends(get_current_user),
) -> str:
    """
    Get just the current user's ID.

    LEARNING NOTE:
    Sometimes you only need the user ID, not the full user object.
    This is a convenience dependency.
    """
    return user.id
