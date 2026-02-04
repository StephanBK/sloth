"""
Pydantic Schemas Package

LEARNING NOTE:
Schemas (also called "DTOs" - Data Transfer Objects) define the shape
of data going in and out of your API. They're different from models:

- Models = Database tables (SQLAlchemy)
- Schemas = API request/response shapes (Pydantic)

Why separate? Because what you store in the database often differs
from what you send to/receive from the client.

TUTORIAL: https://fastapi.tiangolo.com/tutorial/body/
"""

from app.schemas.meal_plan import (
    MealPlanBase,
    MealPlanCreate,
    MealPlanResponse,
    MealPlanListResponse,
    MealResponse,
    IngredientResponse,
)

__all__ = [
    "MealPlanBase",
    "MealPlanCreate",
    "MealPlanResponse",
    "MealPlanListResponse",
    "MealResponse",
    "IngredientResponse",
]
