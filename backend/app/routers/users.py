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
    current_user.starting_weight_kg = intake_data.current_weight_kg  # Capture starting weight

    # Convert list to comma-separated string for storage
    if intake_data.dietary_restrictions:
        current_user.dietary_restrictions = ','.join(intake_data.dietary_restrictions)

    # Calculate starting level based on calorie awareness
    current_user.current_level = calculate_starting_level(
        gender=intake_data.gender,
        current_weight_kg=intake_data.current_weight_kg,
        calorie_awareness=intake_data.calorie_awareness,
        known_calorie_intake=intake_data.known_calorie_intake,
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

    if screen_data.dietary_restrictions:
        current_user.dietary_restrictions = ','.join(screen_data.dietary_restrictions)

    # Calculate starting level based on calorie awareness
    current_user.current_level = calculate_starting_level(
        gender=current_user.gender,
        current_weight_kg=current_user.current_weight_kg,
        calorie_awareness=screen_data.calorie_awareness,
        known_calorie_intake=screen_data.known_calorie_intake,
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
    current_weight_kg: float,
    calorie_awareness: str,
    known_calorie_intake: int = None,
) -> int:
    """
    Calculate the starting diet level based on calorie awareness.

    Calorie levels per gender:
      Men:   Level 1=2700, Level 2=2400, Level 3=2100, Level 4=1800, Level 5=1500
      Women: Level 1=2400, Level 2=2100, Level 3=1800, Level 4=1500, Level 5=1200

    Logic:
    1. If user knows their calorie intake:
       - Find the next level DOWN from their reported intake
       - "gaining" → the level at or just below their intake (they need less)
       - "maintaining" → one level below their intake (create a deficit)
       - "losing" → the level closest to their intake (they're already in deficit)

    2. If user doesn't know ("unknown"):
       - Estimate: body weight (kg) × 30 = approximate maintenance calories
       - Pick the next calorie level down from that estimate

    The starting point doesn't need to be perfect — the system
    auto-corrects weekly via stall detection.
    """
    # Define calorie levels by gender
    if gender == "female":
        calorie_levels = {1: 2400, 2: 2100, 3: 1800, 4: 1500, 5: 1200}
    else:
        calorie_levels = {1: 2700, 2: 2400, 3: 2100, 4: 1800, 5: 1500}

    if calorie_awareness == "unknown" or known_calorie_intake is None:
        # Estimate: body weight × 30
        estimated_maintenance = current_weight_kg * 30
        target_calories = estimated_maintenance
    else:
        target_calories = known_calorie_intake

    # For gaining/unknown: pick the level at or just below the target
    # For maintaining: pick one step below (create deficit)
    # For losing: pick the level closest to what they're already eating
    def find_level_at_or_below(target: float) -> int:
        """Find the highest level (lowest number) whose calories are <= target."""
        for level in sorted(calorie_levels.keys()):
            if calorie_levels[level] <= target:
                return level
        # If target is below all levels, return level 5 (lowest calories)
        return 5

    def find_closest_level(target: float) -> int:
        """Find the level whose calories are closest to target."""
        closest_level = 1
        closest_diff = abs(calorie_levels[1] - target)
        for level, kcal in calorie_levels.items():
            diff = abs(kcal - target)
            if diff < closest_diff:
                closest_diff = diff
                closest_level = level
        return closest_level

    if calorie_awareness == "losing":
        # Already in deficit — match their current intake
        return find_closest_level(target_calories)
    elif calorie_awareness == "maintaining":
        # At maintenance — go one step below
        level = find_level_at_or_below(target_calories)
        return min(level + 1, 5)  # One step more aggressive, cap at 5
    else:
        # gaining or unknown — pick the level at or just below
        return find_level_at_or_below(target_calories)
