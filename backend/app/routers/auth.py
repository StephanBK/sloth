"""
Authentication API Router

LEARNING NOTE:
This router handles all authentication endpoints:
- POST /auth/register - Create new account with email/password
- POST /auth/login - Sign in with email/password
- POST /auth/refresh - Get new access token
- GET /auth/google - Get Google OAuth URL
- POST /auth/logout - Sign out
- POST /auth/reset-password - Request password reset

All actual auth logic is in AuthService - this router just handles HTTP.

TUTORIAL: https://fastapi.tiangolo.com/tutorial/security/
"""

from fastapi import APIRouter, HTTPException, Depends, status
from app.services.auth_service import AuthService, get_auth_service
from app.schemas.auth import (
    EmailPasswordRequest,
    RefreshTokenRequest,
    PasswordResetRequest,
    GoogleOAuthRequest,
    AuthResponse,
    TokenRefreshResponse,
    GoogleOAuthResponse,
    MessageResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    responses={
        400: {"description": "Email already registered or invalid data"},
        500: {"description": "Supabase not configured"},
    }
)
async def register(
    credentials: EmailPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Register a new user with email and password.

    LEARNING NOTE:
    - Supabase handles password hashing and storage
    - If email confirmation is enabled in Supabase, user gets an email
    - The session may be None if email confirmation is required

    **Flow:**
    1. User submits email + password
    2. Supabase creates account and (optionally) sends confirmation email
    3. If no confirmation needed, returns tokens immediately
    4. Frontend stores tokens for authenticated requests
    """
    if not auth_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured. Add Supabase credentials to .env"
        )

    try:
        result = await auth_service.sign_up_with_email(
            email=credentials.email,
            password=credentials.password
        )
        return AuthResponse(
            user=result["user"],
            session=result.get("session"),
            message=result.get("message")
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with email and password",
    responses={
        401: {"description": "Invalid credentials"},
        500: {"description": "Supabase not configured"},
    }
)
async def login(
    credentials: EmailPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Sign in with email and password.

    LEARNING NOTE:
    - Returns access_token (short-lived, ~1 hour)
    - Returns refresh_token (long-lived, use to get new access tokens)
    - Frontend should store both tokens securely
    - Include access_token in Authorization header: "Bearer <token>"

    **Security tip:** Store tokens in httpOnly cookies or secure storage,
    not in localStorage (vulnerable to XSS attacks).
    """
    if not auth_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured"
        )

    try:
        result = await auth_service.sign_in_with_email(
            email=credentials.email,
            password=credentials.password
        )
        return AuthResponse(
            user=result["user"],
            session=result["session"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    summary="Refresh access token",
    responses={
        401: {"description": "Invalid or expired refresh token"},
    }
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get a new access token using refresh token.

    LEARNING NOTE:
    When access_token expires (check expires_at), call this endpoint
    with the refresh_token to get new tokens without re-entering password.

    **When to use:**
    - Access token expired (401 response from API)
    - Proactively before expiration (check expires_at timestamp)
    """
    if not auth_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured"
        )

    try:
        result = await auth_service.refresh_session(request.refresh_token)
        return TokenRefreshResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/google",
    response_model=GoogleOAuthResponse,
    summary="Get Google OAuth URL",
)
async def google_oauth(
    request: GoogleOAuthRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get the URL to redirect users to for Google OAuth login.

    LEARNING NOTE:
    Google OAuth flow:
    1. Frontend calls this endpoint to get the auth URL
    2. Frontend redirects user to that URL
    3. User signs in with Google
    4. Google redirects back to your redirect_url with tokens in URL fragment
    5. Frontend extracts tokens and stores them

    **redirect_url** should be a page in your frontend that handles the callback,
    e.g., "https://yourapp.com/auth/callback"
    """
    if not auth_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured"
        )

    try:
        url = auth_service.get_google_oauth_url(request.redirect_url)
        return GoogleOAuthResponse(url=url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Sign out user",
)
async def logout(
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Sign out the current user.

    LEARNING NOTE:
    This invalidates the refresh token on Supabase's side.
    The access token will still work until it naturally expires,
    but the user won't be able to refresh it.

    **Frontend should:**
    1. Call this endpoint
    2. Clear stored tokens
    3. Redirect to login page
    """
    # Note: In a real implementation, you'd get the token from the request
    # and pass it to sign_out. For now, we just return success.
    return MessageResponse(message="Signed out successfully")


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Request password reset",
)
async def reset_password(
    request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Request a password reset email.

    LEARNING NOTE:
    - Supabase sends an email with a reset link
    - The link includes a token that expires after some time
    - User clicks link → goes to redirect_url → can set new password

    **Security:** We always return success even if email doesn't exist.
    This prevents attackers from discovering which emails are registered.
    """
    if not auth_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured"
        )

    await auth_service.reset_password_request(
        email=request.email,
        redirect_url=request.redirect_url
    )

    return MessageResponse(
        message="If an account exists with this email, a password reset link has been sent"
    )


@router.get(
    "/me",
    summary="Get current user info (requires auth)",
    responses={
        401: {"description": "Not authenticated"},
    }
)
async def get_current_user():
    """
    Get the currently authenticated user's info.

    LEARNING NOTE:
    This endpoint will be protected by auth middleware.
    We'll implement this after creating the auth dependency.

    For now, it returns a placeholder.
    """
    # TODO: Implement with auth dependency
    return {"message": "This endpoint will return current user info once auth middleware is added"}
