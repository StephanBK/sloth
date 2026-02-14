"""
Meal Plan Models - MealPlan, Meal, and Ingredient

LEARNING NOTE:
This file shows one-to-many relationships:
- One MealPlan has many Meals
- One Meal has many Ingredients

This is the core of your brother's diet system - the 100 pre-built day plans.

TUTORIAL: https://docs.sqlalchemy.org/en/20/tutorial/orm_related_objects.html
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.user import Gender
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product


class MealType(str, enum.Enum):
    """Types of meals in a day plan"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class MealPlan(Base):
    """
    A single day's meal plan.

    Your brother has 100 of these:
    - 50 for men (5 levels x 10 days)
    - 50 for women (5 levels x 10 days)

    Each plan contains multiple meals (breakfast, lunch, dinner, snacks).
    """
    __tablename__ = "meal_plans"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Which level this plan belongs to (1-5)
    level: Mapped[int] = mapped_column(Integer, nullable=False)

    # Day number within the level (1-10)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Which gender this plan is for
    gender: Mapped[Gender] = mapped_column(SQLEnum(Gender), nullable=False)

    # Daily totals (pre-calculated for display)
    total_kcal: Mapped[int] = mapped_column(Integer, nullable=False)
    total_protein: Mapped[float] = mapped_column(Float, nullable=False)
    total_carbs: Mapped[float] = mapped_column(Float, nullable=False)
    total_fat: Mapped[float] = mapped_column(Float, nullable=False)

    # Optional name/description
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Full file path to the PDF for this meal plan
    pdf_path: Mapped[str] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # RELATIONSHIP: One MealPlan has many Meals
    # LEARNING NOTE:
    # - relationship() creates a convenient way to access related objects
    # - back_populates creates a two-way link (meal.meal_plan also works)
    # - cascade="all, delete-orphan" means deleting a plan deletes its meals
    meals: Mapped[list["Meal"]] = relationship(
        "Meal",
        back_populates="meal_plan",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MealPlan {self.gender.value} L{self.level} D{self.day_number} ({self.total_kcal}kcal)>"


class Meal(Base):
    """
    A single meal within a day plan (breakfast, lunch, dinner, snack).

    Contains multiple ingredients with quantities.
    """
    __tablename__ = "meals"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Which meal plan this belongs to
    # LEARNING NOTE: ForeignKey creates the database-level relationship
    meal_plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("meal_plans.id", ondelete="CASCADE"),
        nullable=False
    )

    # Type of meal
    meal_type: Mapped[MealType] = mapped_column(SQLEnum(MealType), nullable=False)

    # Order for display (allows multiple snacks)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # Optional preparation instructions
    instructions: Mapped[str] = mapped_column(Text, nullable=True)

    # Meal totals (pre-calculated)
    total_kcal: Mapped[int] = mapped_column(Integer, default=0)
    total_protein: Mapped[float] = mapped_column(Float, default=0)
    total_carbs: Mapped[float] = mapped_column(Float, default=0)
    total_fat: Mapped[float] = mapped_column(Float, default=0)

    # RELATIONSHIPS
    meal_plan: Mapped["MealPlan"] = relationship("MealPlan", back_populates="meals")
    ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient",
        back_populates="meal",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Meal {self.meal_type.value} ({self.total_kcal}kcal)>"


class Ingredient(Base):
    """
    A single ingredient within a meal.

    Example: "400g Chicken Minutenschnitzel"

    LEARNING NOTE:
    Storing macros per ingredient allows:
    - Recalculating totals if quantities change
    - Future: smart substitutions with macro matching
    """
    __tablename__ = "ingredients"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Which meal this belongs to
    meal_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("meals.id", ondelete="CASCADE"),
        nullable=False
    )

    # Product details
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)  # "g", "ml", "EL", "Stück"

    # Nutritional info for this quantity
    kcal: Mapped[int] = mapped_column(Integer, default=0)
    protein: Mapped[float] = mapped_column(Float, default=0)
    carbs: Mapped[float] = mapped_column(Float, default=0)
    fat: Mapped[float] = mapped_column(Float, default=0)

    # Display order
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # Optional link to the products catalog
    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id"),
        nullable=True,
    )

    # RELATIONSHIPS
    meal: Mapped["Meal"] = relationship("Meal", back_populates="ingredients")
    product: Mapped["Product"] = relationship("Product", back_populates="ingredients")

    def __repr__(self) -> str:
        return f"<Ingredient {self.quantity}{self.unit} {self.product_name}>"
