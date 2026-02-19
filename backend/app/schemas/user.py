"""
User Profile Schemas - API Request/Response Models

LEARNING NOTE:
These schemas handle:
1. Intake form submission (new users)
2. Profile updates (existing users)
3. Profile responses (what we send back)

We separate "create" from "update" schemas because:
- Create requires certain fields
- Update allows partial updates (only send what changed)
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    """Gender options"""
    MALE = "male"
    FEMALE = "female"


class ActivityLevel(str, Enum):
    """Activity level options (kept for backward compatibility)"""
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"


class CalorieAwareness(str, Enum):
    """How the user's current calorie intake relates to their weight"""
    GAINING = "gaining"
    MAINTAINING = "maintaining"
    LOSING = "losing"
    UNKNOWN = "unknown"


# =============================================================================
# Intake Form Schemas (for new users)
# =============================================================================

class IntakeScreen1(BaseModel):
    """
    Screen 1 of intake: Basic info

    LEARNING NOTE:
    We validate ranges to catch obvious errors:
    - Height: 100-250 cm (reasonable human range)
    - Age: 16-100 (app is for adults)
    """
    gender: Gender
    height_cm: int = Field(..., ge=100, le=250, description="Height in cm (100-250)")
    age: int = Field(..., ge=16, le=100, description="Age in years (16-100)")


class IntakeScreen2(BaseModel):
    """
    Screen 2 of intake: Weight info (just current weight)
    """
    current_weight_kg: float = Field(..., ge=30, le=300, description="Current weight in kg")


class IntakeScreen3(BaseModel):
    """
    Screen 3 of intake: Calorie awareness & Diet

    The user either knows their approximate daily calorie intake
    (and whether they're gaining/maintaining/losing at that level),
    or they don't know — in which case we estimate from body weight.
    """
    calorie_awareness: CalorieAwareness = Field(
        ..., description="How the user's current calories relate to their weight"
    )
    known_calorie_intake: Optional[int] = Field(
        default=None, ge=800, le=5000,
        description="Approximate daily calorie intake if known"
    )
    dietary_restrictions: Optional[List[str]] = Field(
        default=None,
        description="List of dietary restrictions (e.g., ['vegetarian', 'gluten-free'])"
    )


class IntakeComplete(BaseModel):
    """
    Complete intake form - all screens combined.

    Use this if you want to submit everything at once.
    """
    # Screen 1
    gender: Gender
    height_cm: int = Field(..., ge=100, le=250)
    age: int = Field(..., ge=16, le=100)

    # Screen 2
    current_weight_kg: float = Field(..., ge=30, le=300)

    # Screen 3
    calorie_awareness: CalorieAwareness
    known_calorie_intake: Optional[int] = Field(default=None, ge=800, le=5000)
    dietary_restrictions: Optional[List[str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "gender": "male",
                    "height_cm": 180,
                    "age": 30,
                    "current_weight_kg": 85.5,
                    "calorie_awareness": "maintaining",
                    "known_calorie_intake": 2400,
                    "dietary_restrictions": ["gluten-free"]
                }
            ]
        }
    }


# =============================================================================
# Profile Update Schemas
# =============================================================================

class ProfileUpdate(BaseModel):
    """
    Update user profile - all fields optional.

    LEARNING NOTE:
    Using Optional[type] = None means the field won't be updated if not provided.
    This is called a "partial update" or "PATCH" style update.
    """
    gender: Optional[Gender] = None
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    age: Optional[int] = Field(None, ge=16, le=100)
    current_weight_kg: Optional[float] = Field(None, ge=30, le=300)
    dietary_restrictions: Optional[List[str]] = None
    current_level: Optional[int] = Field(None, ge=1, le=5)


# =============================================================================
# Response Schemas
# =============================================================================

class UserProfileResponse(BaseModel):
    """
    Full user profile response.

    LEARNING NOTE:
    This is what we return when someone asks for their profile.
    Includes computed fields like BMI that aren't stored in DB.
    """
    id: str
    email: str

    # Profile fields
    gender: Optional[Gender] = None
    height_cm: Optional[int] = None
    age: Optional[int] = None
    current_weight_kg: Optional[float] = None
    goal_weight_kg: Optional[float] = None
    starting_weight_kg: Optional[float] = None
    activity_level: Optional[ActivityLevel] = None
    dietary_restrictions: Optional[List[str]] = None

    # Diet settings
    current_level: int

    # App state
    intake_completed: bool
    profile_picture_url: Optional[str] = None

    # Computed fields (calculated, not stored)
    bmi: Optional[float] = None
    weight_to_lose: Optional[float] = None
    total_weight_lost: Optional[float] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_user(cls, user) -> "UserProfileResponse":
        """
        Create response from User model.

        LEARNING NOTE:
        We need this custom method to:
        1. Convert dietary_restrictions string to list
        2. Include computed properties (bmi, etc.)
        """
        # Convert comma-separated string to list
        restrictions = None
        if user.dietary_restrictions:
            restrictions = [r.strip() for r in user.dietary_restrictions.split(',') if r.strip()]

        return cls(
            id=user.id,
            email=user.email,
            gender=user.gender,
            height_cm=user.height_cm,
            age=user.age,
            current_weight_kg=user.current_weight_kg,
            goal_weight_kg=user.goal_weight_kg,
            starting_weight_kg=user.starting_weight_kg,
            activity_level=user.activity_level,
            dietary_restrictions=restrictions,
            current_level=user.current_level,
            intake_completed=user.intake_completed,
            profile_picture_url=user.profile_picture_url,
            bmi=user.bmi,
            weight_to_lose=user.weight_to_lose,
            total_weight_lost=user.total_weight_lost,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UserPublicResponse(BaseModel):
    """
    Minimal public user info (for leaderboards, etc. - future feature)
    """
    id: str
    current_level: int
    total_weight_lost: Optional[float] = None

    model_config = {"from_attributes": True}
