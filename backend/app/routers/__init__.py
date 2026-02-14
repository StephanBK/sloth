"""
API Routers Package

LEARNING NOTE:
FastAPI uses "routers" to organize your API into logical groups.
Think of them like folders for your endpoints:

- /meal-plans → meal_plans.py
- /users → users.py
- /progress → progress.py

This keeps your code organized as the API grows.

TUTORIAL: https://fastapi.tiangolo.com/tutorial/bigger-applications/
"""

from app.routers.meal_plans import router as meal_plans_router
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router

__all__ = ["meal_plans_router", "auth_router", "products_router"]
