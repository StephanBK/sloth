"""
Database Models Package

LEARNING NOTE:
This __init__.py file imports all models so they can be accessed easily:
    from app.models import User, MealPlan, Meal, Ingredient

It also ensures all models are registered with SQLAlchemy's Base
before we run migrations.
"""

from app.models.user import User
from app.models.meal_plan import MealPlan, Meal, Ingredient
from app.models.progress import WeightEntry
from app.models.preference import UserPreference

# This list is used by Alembic to detect all models
__all__ = [
    "User",
    "MealPlan",
    "Meal",
    "Ingredient",
    "WeightEntry",
    "UserPreference",
]
