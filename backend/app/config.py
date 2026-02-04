"""
Application configuration using Pydantic Settings.

LEARNING NOTE:
- Pydantic Settings automatically reads from environment variables
- The .env file is loaded via python-dotenv
- This pattern keeps secrets out of code and makes deployment easier

TUTORIAL: https://fastapi.tiangolo.com/advanced/settings/
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Create a .env file in the backend/ directory with these values:

    DATABASE_URL=postgresql://user:password@localhost:5432/sloth
    SECRET_KEY=your-secret-key-here
    ENVIRONMENT=development
    """

    # Database
    database_url: str = "postgresql://sloth_user:password@localhost:5432/sloth"

    # Security
    secret_key: str = "change-this-in-production-use-a-real-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Environment
    environment: str = "development"
    debug: bool = True

    # Supabase Auth
    # Get these from: Supabase Dashboard → Settings → API
    supabase_url: str = ""  # e.g., "https://xxxxx.supabase.co"
    supabase_anon_key: str = ""  # The "anon/public" key
    supabase_service_role_key: str = ""  # The "service_role" key (keep secret!)

    # Supabase JWT Secret (for verifying tokens server-side)
    # Get this from: Supabase Dashboard → Settings → API → JWT Settings
    supabase_jwt_secret: str = ""

    # Stripe Payment Settings
    # Get these from: https://dashboard.stripe.com/apikeys
    stripe_secret_key: str = ""  # sk_test_... or sk_live_...
    stripe_publishable_key: str = ""  # pk_test_... or pk_live_...
    stripe_webhook_secret: str = ""  # whsec_... (from webhook settings)

    # Stripe Price IDs (create these in Stripe Dashboard → Products)
    stripe_price_monthly: str = ""  # price_... for monthly subscription
    stripe_price_yearly: str = ""  # price_... for yearly subscription

    # App URL for Stripe redirects
    frontend_url: str = "http://localhost:5173"

    # Future: Claude API (uncomment when ready)
    # claude_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.

    LEARNING NOTE:
    - @lru_cache() means this function only runs once
    - Subsequent calls return the cached Settings object
    - This is efficient and avoids re-reading .env on every request
    """
    return Settings()
