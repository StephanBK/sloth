"""
Authentication Schemas - API Request/Response Models

LEARNING NOTE:
These schemas define what data the auth endpoints accept and return.
Pydantic validates all incoming data automatically.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# =============================================================================
# Request Schemas (what the client sends)
# =============================================================================

class EmailPasswordRequest(BaseModel):
    """
    Schema for email/password login and registration.

    LEARNING NOTE:
    - EmailStr is a special Pydantic type that validates email format
    - Field(...) with min_length ensures password isn't empty
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "securepassword123"
                }
            ]
        }
    }


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing access token"""
    refresh_token: str = Field(..., description="The refresh token from login")


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""
    email: EmailStr = Field(..., description="Email to send reset link to")
    redirect_url: str = Field(..., description="URL to redirect after reset")


class GoogleOAuthRequest(BaseModel):
    """Schema for initiating Google OAuth"""
    redirect_url: str = Field(
        ...,
        description="URL to redirect after Google authentication"
    )


class OAuthCodeExchangeRequest(BaseModel):
    """Schema for exchanging OAuth authorization code for tokens"""
    code: str = Field(..., description="The authorization code from OAuth callback")


# =============================================================================
# Response Schemas (what the server returns)
# =============================================================================

class UserResponse(BaseModel):
    """Basic user info returned in responses"""
    id: str
    email: str
    email_confirmed: Optional[bool] = None


class SessionResponse(BaseModel):
    """Session/token info returned after login"""
    access_token: str
    refresh_token: str
    expires_at: Optional[int] = None  # Unix timestamp


class AuthResponse(BaseModel):
    """
    Full auth response with user and session.

    LEARNING NOTE:
    This is what gets returned after successful login/signup.
    The frontend stores these tokens and includes access_token
    in the Authorization header for subsequent requests.
    """
    user: UserResponse
    session: Optional[SessionResponse] = None
    message: Optional[str] = None


class TokenRefreshResponse(BaseModel):
    """Response after refreshing tokens"""
    access_token: str
    refresh_token: str
    expires_at: Optional[int] = None


class GoogleOAuthResponse(BaseModel):
    """Response with Google OAuth URL"""
    url: str
    message: str = "Redirect user to this URL for Google authentication"


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    success: bool = True


# =============================================================================
# Error Response
# =============================================================================

class AuthErrorResponse(BaseModel):
    """Error response for auth failures"""
    detail: str
    error_code: Optional[str] = None
