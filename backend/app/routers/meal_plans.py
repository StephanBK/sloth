"""
Meal Plans API Router

LEARNING NOTE:
This file contains all the endpoints related to meal plans:
- GET /meal-plans - List all meal plans (with filters)
- GET /meal-plans/{id} - Get a specific meal plan with full details
- POST /meal-plans - Create a new meal plan (admin only, later)

Key concepts:
1. Path parameters: /meal-plans/{id} - the {id} becomes a function argument
2. Query parameters: ?level=1&gender=male - optional filters
3. Dependency injection: Depends(get_db) provides database session

TUTORIAL: https://fastapi.tiangolo.com/tutorial/path-params/
TUTORIAL: https://fastapi.tiangolo.com/tutorial/query-params/
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.database import get_db
from app.models.meal_plan import MealPlan, Meal, Ingredient
from app.models.user import Gender
from app.schemas.meal_plan import (
    MealPlanResponse,
    MealPlanListResponse,
    MealPlanCreate,
)

# Create the router
# LEARNING NOTE: prefix="/meal-plans" means all routes here start with /meal-plans
# tags=["Meal Plans"] groups these in the API documentation
router = APIRouter(
    prefix="/meal-plans",
    tags=["Meal Plans"],
)


@router.get("", response_model=list[MealPlanListResponse])
async def list_meal_plans(
    db: Session = Depends(get_db),
    level: Optional[int] = Query(None, ge=1, le=5, description="Filter by diet level"),
    gender: Optional[Gender] = Query(None, description="Filter by gender"),
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination)"),
    limit: int = Query(100, ge=1, le=100, description="Max records to return"),
):
    """
    List all meal plans with optional filters.

    LEARNING NOTE:
    - Query() defines query parameters with validation
    - Optional[int] means the parameter is not required
    - ge=1 means "greater than or equal to 1"
    - The docstring becomes the endpoint description in /docs

    Example URLs:
    - GET /meal-plans - All plans
    - GET /meal-plans?level=1 - Level 1 plans only
    - GET /meal-plans?gender=male&level=2 - Male, Level 2 plans
    """
    # Start building the query
    query = db.query(MealPlan)

    # Apply filters if provided
    if level is not None:
        query = query.filter(MealPlan.level == level)
    if gender is not None:
        query = query.filter(MealPlan.gender == gender)

    # Order by level, then day number for logical display
    query = query.order_by(MealPlan.level, MealPlan.day_number)

    # Apply pagination
    meal_plans = query.offset(skip).limit(limit).all()

    return meal_plans


@router.get("/{meal_plan_id}", response_model=MealPlanResponse)
async def get_meal_plan(
    meal_plan_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific meal plan with all meals and ingredients.

    LEARNING NOTE:
    - {meal_plan_id} in the path becomes a function parameter
    - joinedload() tells SQLAlchemy to fetch related data in ONE query
      instead of making separate queries (this is called "eager loading")
    - HTTPException with 404 is the standard way to say "not found"

    Without joinedload, accessing meal_plan.meals would trigger
    additional database queries (called "N+1 problem").
    """
    # Eager load meals and ingredients to avoid N+1 queries
    meal_plan = (
        db.query(MealPlan)
        .options(
            joinedload(MealPlan.meals).joinedload(Meal.ingredients)
        )
        .filter(MealPlan.id == meal_plan_id)
        .first()
    )

    if meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    return meal_plan


@router.post("", response_model=MealPlanResponse, status_code=201)
async def create_meal_plan(
    meal_plan_data: MealPlanCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new meal plan with meals and ingredients.

    LEARNING NOTE:
    - The request body is automatically parsed into MealPlanCreate
    - Pydantic validates the data before this function runs
    - If validation fails, FastAPI returns a 422 error automatically
    - status_code=201 means "Created" (better than default 200 for POST)

    This endpoint will later be restricted to admin users only.
    """
    # Create the meal plan
    meal_plan = MealPlan(
        level=meal_plan_data.level,
        day_number=meal_plan_data.day_number,
        gender=meal_plan_data.gender,
        total_kcal=meal_plan_data.total_kcal,
        total_protein=meal_plan_data.total_protein,
        total_carbs=meal_plan_data.total_carbs,
        total_fat=meal_plan_data.total_fat,
        name=meal_plan_data.name,
        description=meal_plan_data.description,
    )

    # Create meals and ingredients
    for meal_data in meal_plan_data.meals:
        meal = Meal(
            meal_type=meal_data.meal_type,
            order_index=meal_data.order_index,
            instructions=meal_data.instructions,
            total_kcal=sum(i.kcal for i in meal_data.ingredients),
            total_protein=sum(i.protein for i in meal_data.ingredients),
            total_carbs=sum(i.carbs for i in meal_data.ingredients),
            total_fat=sum(i.fat for i in meal_data.ingredients),
        )

        # Create ingredients for this meal
        for ing_data in meal_data.ingredients:
            ingredient = Ingredient(
                product_name=ing_data.product_name,
                quantity=ing_data.quantity,
                unit=ing_data.unit,
                kcal=ing_data.kcal,
                protein=ing_data.protein,
                carbs=ing_data.carbs,
                fat=ing_data.fat,
                order_index=ing_data.order_index,
            )
            meal.ingredients.append(ingredient)

        meal_plan.meals.append(meal)

    # Save to database
    db.add(meal_plan)
    db.commit()
    db.refresh(meal_plan)

    return meal_plan
