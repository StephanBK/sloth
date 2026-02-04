"""
User Model

LEARNING NOTE:
This defines the 'users' table in your database. Key concepts:

1. Column types (String, Integer, etc.) map to PostgreSQL types
2. Primary keys uniquely identify each row
3. Indexes speed up searches on frequently-queried columns
4. Relationships link tables together
5. nullable=True means the field is optional

TUTORIAL: https://docs.sqlalchemy.org/en/20/tutorial/metadata.html
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, Boolean, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class Gender(str, enum.Enum):
    """
    LEARNING NOTE:
    Python Enum + str inheritance means these values serialize to strings.
    In the database, this becomes a PostgreSQL ENUM type.
    """
    MALE = "male"
    FEMALE = "female"


class ActivityLevel(str, enum.Enum):
    """
    Activity level for calorie calculations.

    LEARNING NOTE:
    These map to standard TDEE (Total Daily Energy Expenditure) multipliers:
    - Sedentary: 1.2 (desk job, no exercise)
    - Light: 1.375 (light exercise 1-3 days/week)
    - Moderate: 1.55 (moderate exercise 3-5 days/week)
    - Active: 1.725 (hard exercise 6-7 days/week)
    """
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"


class User(Base):
    """
    User account model.

    LEARNING NOTE:
    - __tablename__ sets the actual table name in PostgreSQL
    - Mapped[type] is the modern SQLAlchemy 2.0 type hint syntax
    - mapped_column() defines column properties
    - Optional fields use Mapped[Optional[type]] and nullable=True
    """
    __tablename__ = "users"

    # ===========================================================================
    # Core Fields (from Supabase Auth)
    # ===========================================================================

    # Primary key - matches Supabase Auth user ID
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # User email - must be unique, indexed for fast lookups
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    # ===========================================================================
    # Profile Fields (from Intake Form)
    # ===========================================================================

    # Gender determines which meal plans to show (men vs women)
    gender: Mapped[Optional[Gender]] = mapped_column(
        SQLEnum(Gender),
        nullable=True  # Nullable until intake form completed
    )

    # Physical stats
    height_cm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    # Weight tracking
    current_weight_kg: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    goal_weight_kg: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    # Starting weight - captured at intake, never changes
    # Useful for showing total progress
    starting_weight_kg: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    # Activity level for calorie calculations
    activity_level: Mapped[Optional[ActivityLevel]] = mapped_column(
        SQLEnum(ActivityLevel),
        nullable=True
    )

    # ===========================================================================
    # Diet Settings
    # ===========================================================================

    # Current diet level (1-5)
    # Level 1 = highest calories, Level 5 = lowest (most aggressive deficit)
    current_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    # Dietary restrictions - stored as comma-separated values
    # e.g., "vegetarian,gluten-free"
    # LEARNING NOTE: For MVP, simple string. Later could be a separate table.
    dietary_restrictions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # ===========================================================================
    # App State
    # ===========================================================================

    # Has the user completed the intake form?
    # LEARNING NOTE: This flag tells the frontend whether to show intake or main app
    intake_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Profile picture URL (future feature)
    profile_picture_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    # ===========================================================================
    # Stripe/Subscription Fields
    # ===========================================================================

    # Stripe customer ID - linked after first purchase
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    # Subscription status for quick checks (updated by webhooks)
    subscription_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="none"
    )

    # When current subscription period ends (for UI display)
    subscription_ends_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    # ===========================================================================
    # Timestamps
    # ===========================================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ===========================================================================
    # Relationships
    # ===========================================================================

    # One user has many weight entries
    weight_entries: Mapped[list["WeightEntry"]] = relationship(
        "WeightEntry",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # One user has many preferences
    preferences: Mapped[list["UserPreference"]] = relationship(
        "UserPreference",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<User {self.email} level={self.current_level}>"

    @property
    def bmi(self) -> Optional[float]:
        """
        Calculate BMI if we have height and weight.

        LEARNING NOTE:
        BMI = weight(kg) / height(m)²
        This is a @property - it's calculated on the fly, not stored in DB.
        """
        if self.current_weight_kg and self.height_cm:
            height_m = self.height_cm / 100
            return round(self.current_weight_kg / (height_m ** 2), 1)
        return None

    @property
    def weight_to_lose(self) -> Optional[float]:
        """How much weight left to lose to reach goal"""
        if self.current_weight_kg and self.goal_weight_kg:
            diff = self.current_weight_kg - self.goal_weight_kg
            return round(diff, 1) if diff > 0 else 0
        return None

    @property
    def total_weight_lost(self) -> Optional[float]:
        """Total weight lost since starting"""
        if self.starting_weight_kg and self.current_weight_kg:
            diff = self.starting_weight_kg - self.current_weight_kg
            return round(diff, 1) if diff > 0 else 0
        return None
