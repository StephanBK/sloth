"""
Services Package

LEARNING NOTE:
Services contain business logic that doesn't belong in routes.
This separation makes your code:
- Easier to test (test service functions directly)
- More reusable (call from multiple routes)
- Cleaner (routes just handle HTTP, services handle logic)
"""

from app.services.auth_service import AuthService, get_auth_service

__all__ = ["AuthService", "get_auth_service"]
