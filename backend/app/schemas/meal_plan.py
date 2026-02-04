"""
Meal Plan Schemas - API Request/Response Models

LEARNING NOTE:
Pydantic schemas serve multiple purposes:
1. Validate incoming data (automatic error responses if invalid)
2. Document the API (shown in /docs)
3. Serialize outgoing data (convert DB objects to JSON)

Notice the naming convention:
- *Base: Shared fields
- *Create: Fields needed when creating
- *Response: Fields returned to client

TUTORIAL: https://fastapi.tiangolo.com/tutorial/schema-extra-example/
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    """Gender enum for API"""
    MALE = "male"
    FEMALE = "female"


class MealType(str, Enum):
    """Meal type enum for API"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


# =============================================================================
# Ingredient Schemas
# =============================================================================

class IngredientBase(BaseModel):
    """Base ingredient fields"""
    product_name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    kcal: int = Field(default=0, ge=0)
    protein: float = Field(default=0, ge=0)
    carbs: float = Field(default=0, ge=0)
    fat: float = Field(default=0, ge=0)


class IngredientCreate(IngredientBase):
    """Schema for creating an ingredient"""
    order_index: int = Field(default=0, ge=0)


class IngredientResponse(IngredientBase):
    """
    Schema for ingredient in API responses.

    LEARNING NOTE:
    model_config with from_attributes=True tells Pydantic to read
    attributes from SQLAlchemy model objects, not just dictionaries.
    """
    id: str
    order_index: int

    model_config = {"from_attributes": True}


# =============================================================================
# Meal Schemas
# =============================================================================

class MealBase(BaseModel):
    """Base meal fields"""
    meal_type: MealType
    order_index: int = Field(default=0, ge=0)
    instructions: Optional[str] = None


class MealCreate(MealBase):
    """Schema for creating a meal"""
    ingredients: list[IngredientCreate] = Field(default_factory=list)


class MealResponse(MealBase):
    """Schema for meal in API responses"""
    id: str
    total_kcal: int
    total_protein: float
    total_carbs: float
    total_fat: float
    ingredients: list[IngredientResponse] = []

    model_config = {"from_attributes": True}


# =============================================================================
# Meal Plan Schemas
# =============================================================================

class MealPlanBase(BaseModel):
    """
    Base meal plan fields.

    LEARNING NOTE:
    Field(...) means the field is required.
    Field(default=X) means optional with a default.
    ge=0 means "greater than or equal to 0" (validation).
    """
    level: int = Field(..., ge=1, le=5, description="Diet level (1=highest calories, 5=lowest)")
    day_number: int = Field(..., ge=1, le=10, description="Day number within level (1-10)")
    gender: Gender
    total_kcal: int = Field(..., ge=0)
    total_protein: float = Field(..., ge=0)
    total_carbs: float = Field(..., ge=0)
    total_fat: float = Field(..., ge=0)
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class MealPlanCreate(MealPlanBase):
    """Schema for creating a meal plan"""
    meals: list[MealCreate] = Field(default_factory=list)


class MealPlanResponse(MealPlanBase):
    """
    Full meal plan response including meals and ingredients.

    LEARNING NOTE:
    This is a "nested" response - the meal plan contains meals,
    and each meal contains ingredients. Pydantic handles the
    serialization automatically.
    """
    id: str
    created_at: datetime
    updated_at: datetime
    meals: list[MealResponse] = []

    model_config = {"from_attributes": True}


class MealPlanListResponse(BaseModel):
    """
    Simplified meal plan for list views (without full meal details).

    LEARNING NOTE:
    For list endpoints, you often don't need all the nested data.
    This lighter response is faster and uses less bandwidth.
    """
    id: str
    level: int
    day_number: int
    gender: Gender
    total_kcal: int
    total_protein: float
    total_carbs: float
    total_fat: float
    name: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
