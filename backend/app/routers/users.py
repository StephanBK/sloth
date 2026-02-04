"""
Users API Router - Profile & Intake Management

LEARNING NOTE:
This router handles:
- GET /users/me - Get current user's profile
- POST /users/me/intake - Complete intake form (new users)
- PATCH /users/me - Update profile (existing users)

All endpoints require authentication.
The "me" pattern is common - it means "the currently logged-in user".

TUTORIAL: https://fastapi.tiangolo.com/tutorial/security/
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.user import (
    IntakeComplete,
    IntakeScreen1,
    IntakeScreen2,
    IntakeScreen3,
    ProfileUpdate,
    UserProfileResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get the currently authenticated user's profile.

    LEARNING NOTE:
    - Depends(get_current_user) extracts and validates the JWT token
    - If token is invalid/missing, it returns 401 automatically
    - current_user is the User model from our database
    """
    return UserProfileResponse.from_user(current_user)


@router.post(
    "/me/intake",
    response_model=UserProfileResponse,
    summary="Complete intake form",
    responses={
        400: {"description": "Intake already completed"},
    }
)
async def complete_intake(
    intake_data: IntakeComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Complete the intake form for a new user.

    LEARNING NOTE:
    This is called once when a user first signs up.
    After this, intake_completed=True and they see the main app.

    The starting_weight_kg is set here and never changes -
    it's used to show total progress over time.
    """
    # Check if intake already completed
    if current_user.intake_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Intake form already completed. Use PATCH /users/me to update profile."
        )

    # Update user with intake data
    current_user.gender = intake_data.gender
    current_user.height_cm = intake_data.height_cm
    current_user.age = intake_data.age
    current_user.current_weight_kg = intake_data.current_weight_kg
    current_user.goal_weight_kg = intake_data.goal_weight_kg
    current_user.starting_weight_kg = intake_data.current_weight_kg  # Capture starting weight
    current_user.activity_level = intake_data.activity_level

    # Convert list to comma-separated string for storage
    if intake_data.dietary_restrictions:
        current_user.dietary_restrictions = ','.join(intake_data.dietary_restrictions)

    # Calculate starting level based on profile
    # TODO: Implement proper level calculation logic
    current_user.current_level = calculate_starting_level(
        gender=intake_data.gender,
        activity_level=intake_data.activity_level,
        current_weight_kg=intake_data.current_weight_kg,
        goal_weight_kg=intake_data.goal_weight_kg,
    )

    # Mark intake as complete
    current_user.intake_completed = True

    db.commit()
    db.refresh(current_user)

    return UserProfileResponse.from_user(current_user)


@router.post(
    "/me/intake/screen1",
    response_model=dict,
    summary="Save intake screen 1 (partial)",
)
async def save_intake_screen1(
    screen_data: IntakeScreen1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Save just screen 1 of intake (for multi-screen flow).

    LEARNING NOTE:
    This allows saving progress between screens.
    User can close app and resume later.
    intake_completed stays False until all screens done.
    """
    current_user.gender = screen_data.gender
    current_user.height_cm = screen_data.height_cm
    current_user.age = screen_data.age

    db.commit()

    return {"message": "Screen 1 saved", "next": "/users/me/intake/screen2"}


@router.post(
    "/me/intake/screen2",
    response_model=dict,
    summary="Save intake screen 2 (partial)",
)
async def save_intake_screen2(
    screen_data: IntakeScreen2,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save just screen 2 of intake."""
    current_user.current_weight_kg = screen_data.current_weight_kg
    current_user.goal_weight_kg = screen_data.goal_weight_kg
    current_user.starting_weight_kg = screen_data.current_weight_kg

    db.commit()

    return {"message": "Screen 2 saved", "next": "/users/me/intake/screen3"}


@router.post(
    "/me/intake/screen3",
    response_model=UserProfileResponse,
    summary="Save intake screen 3 and complete intake",
)
async def save_intake_screen3(
    screen_data: IntakeScreen3,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Save screen 3 and complete the intake process.

    LEARNING NOTE:
    This is the final screen. After this:
    - intake_completed = True
    - starting_level is calculated
    - User sees the main app
    """
    # Verify previous screens were completed
    if not all([current_user.gender, current_user.height_cm, current_user.current_weight_kg]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete screens 1 and 2 first"
        )

    current_user.activity_level = screen_data.activity_level

    if screen_data.dietary_restrictions:
        current_user.dietary_restrictions = ','.join(screen_data.dietary_restrictions)

    # Calculate starting level
    current_user.current_level = calculate_starting_level(
        gender=current_user.gender,
        activity_level=screen_data.activity_level,
        current_weight_kg=current_user.current_weight_kg,
        goal_weight_kg=current_user.goal_weight_kg,
    )

    current_user.intake_completed = True

    db.commit()
    db.refresh(current_user)

    return UserProfileResponse.from_user(current_user)


@router.patch(
    "/me",
    response_model=UserProfileResponse,
    summary="Update profile",
)
async def update_profile(
    updates: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the current user's profile.

    LEARNING NOTE:
    PATCH means "partial update" - only send the fields you want to change.
    Fields not included in the request are not modified.

    Example: To just update weight, send: {"current_weight_kg": 82.5}
    """
    # Get the fields that were actually provided (not None)
    update_data = updates.model_dump(exclude_unset=True)

    # Handle dietary_restrictions specially (list to string)
    if 'dietary_restrictions' in update_data and update_data['dietary_restrictions'] is not None:
        update_data['dietary_restrictions'] = ','.join(update_data['dietary_restrictions'])

    # Update each provided field
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return UserProfileResponse.from_user(current_user)


def calculate_starting_level(
    gender: str,
    activity_level: str,
    current_weight_kg: float,
    goal_weight_kg: float,
) -> int:
    """
    Calculate the starting diet level based on user profile.

    LEARNING NOTE:
    This is placeholder logic. The real formula should come from
    your brother's Faultierrechner system.

    Current logic:
    - Uses Mifflin-St Jeor formula for BMR
    - Multiplies by activity factor for TDEE
    - Maps to level 1-5 based on deficit needed

    TODO: Replace with actual Faultierdiät calculation
    """
    # Activity multipliers (TDEE = BMR * multiplier)
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
    }

    multiplier = activity_multipliers.get(activity_level, 1.375)

    # For now, simple logic:
    # - If need to lose a lot (>15kg): Start at Level 1 (highest calories, gradual)
    # - If need to lose moderate (8-15kg): Start at Level 2
    # - If need to lose some (3-8kg): Start at Level 3
    # - If need to lose little (<3kg): Start at Level 4

    weight_to_lose = current_weight_kg - goal_weight_kg

    if weight_to_lose > 15:
        return 1
    elif weight_to_lose > 8:
        return 2
    elif weight_to_lose > 3:
        return 3
    else:
        return 4

    # Note: Level 5 is never a starting level - it's only reached
    # after dropping from higher levels due to stalls.
