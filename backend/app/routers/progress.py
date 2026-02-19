"""
Weight Tracking API Router - Progress Management

LEARNING NOTE:
This router handles:
- POST /weight - Log a new weight entry
- GET /weight - Get weight history with stats and stall detection
- GET /weight/{id} - Get single entry
- PATCH /weight/{id} - Update an entry
- DELETE /weight/{id} - Delete an entry

The weight graph is Apple Health-inspired:
- Solid lines between actual measurements
- Dotted lines for gaps (interpolated)
- Shows trend and stall warnings

TUTORIAL: https://fastapi.tiangolo.com/tutorial/sql-databases/
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date, timedelta
from typing import Optional, List

from app.database import get_db
from app.models.user import User
from app.models.progress import WeightEntry
from app.dependencies import get_current_user
from app.schemas.progress import (
    WeightEntryCreate,
    WeightEntryUpdate,
    WeightEntryResponse,
    WeightHistoryResponse,
    WeightHistoryPoint,
    WeightStats,
    StallStatus,
)

router = APIRouter(
    prefix="/weight",
    tags=["Weight Tracking"],
)


# =============================================================================
# Weight Entry CRUD
# =============================================================================

@router.post(
    "",
    response_model=WeightEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a weight entry",
)
async def create_weight_entry(
    entry_data: WeightEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Log a new weight measurement.

    LEARNING NOTE:
    - We prevent duplicate entries for the same date
    - This also updates the user's current_weight_kg to latest
    - If this is first entry, also sets starting_weight_kg
    """
    # Check if entry already exists for this date
    existing = db.query(WeightEntry).filter(
        WeightEntry.user_id == current_user.id,
        WeightEntry.measured_at == entry_data.measured_at
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entry already exists for {entry_data.measured_at}. Use PATCH to update."
        )

    # Create the entry
    new_entry = WeightEntry(
        user_id=current_user.id,
        weight_kg=entry_data.weight_kg,
        measured_at=entry_data.measured_at,
        notes=entry_data.notes,
    )
    db.add(new_entry)

    # Update user's current weight if this is the most recent entry
    latest_entry = db.query(WeightEntry).filter(
        WeightEntry.user_id == current_user.id
    ).order_by(desc(WeightEntry.measured_at)).first()

    if not latest_entry or entry_data.measured_at >= latest_entry.measured_at:
        current_user.current_weight_kg = entry_data.weight_kg

    # If user doesn't have starting weight, set it
    if current_user.starting_weight_kg is None:
        current_user.starting_weight_kg = entry_data.weight_kg

    db.commit()
    db.refresh(new_entry)

    return new_entry


@router.get(
    "",
    response_model=WeightHistoryResponse,
    summary="Get weight history with stats",
)
async def get_weight_history(
    days: int = Query(30, ge=7, le=365, description="Number of days of history"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get weight history with computed stats and stall detection.

    LEARNING NOTE:
    This is the main endpoint for the weight graph screen.
    - Returns actual entries plus interpolated points for gaps
    - Computes progress stats
    - Detects stalls (when to suggest level drop)

    Query params:
    - days: How far back to look (default 30, max 365)
    """
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # Get entries in range, ordered by date
    entries = db.query(WeightEntry).filter(
        WeightEntry.user_id == current_user.id,
        WeightEntry.measured_at >= start_date,
        WeightEntry.measured_at <= end_date
    ).order_by(WeightEntry.measured_at).all()

    # Build history with interpolation for gaps
    history = build_history_with_interpolation(entries, start_date, end_date)

    # Compute stats
    stats = compute_weight_stats(current_user, entries)

    # Detect stalls (looks at last 14 days)
    stall_status = detect_stall(db, current_user)

    return WeightHistoryResponse(
        history=history,
        stats=stats,
        stall_status=stall_status,
        entries=[WeightEntryResponse.model_validate(e) for e in entries],
    )


@router.get(
    "/{entry_id}",
    response_model=WeightEntryResponse,
    summary="Get single weight entry",
)
async def get_weight_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific weight entry by ID."""
    entry = db.query(WeightEntry).filter(
        WeightEntry.id == entry_id,
        WeightEntry.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weight entry not found"
        )

    return entry


@router.patch(
    "/{entry_id}",
    response_model=WeightEntryResponse,
    summary="Update weight entry",
)
async def update_weight_entry(
    entry_id: str,
    updates: WeightEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a weight entry.

    LEARNING NOTE:
    Uses PATCH semantics - only send fields you want to change.
    """
    entry = db.query(WeightEntry).filter(
        WeightEntry.id == entry_id,
        WeightEntry.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weight entry not found"
        )

    # Update only provided fields
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    # If weight changed, may need to update user's current_weight_kg
    if 'weight_kg' in update_data:
        latest = db.query(WeightEntry).filter(
            WeightEntry.user_id == current_user.id
        ).order_by(desc(WeightEntry.measured_at)).first()

        if latest and latest.id == entry_id:
            current_user.current_weight_kg = update_data['weight_kg']

    db.commit()
    db.refresh(entry)

    return entry


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete weight entry",
)
async def delete_weight_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a weight entry.

    LEARNING NOTE:
    Returns 204 No Content on success (REST convention for DELETE).
    """
    entry = db.query(WeightEntry).filter(
        WeightEntry.id == entry_id,
        WeightEntry.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weight entry not found"
        )

    db.delete(entry)
    db.commit()

    # Update current_weight to latest remaining entry
    latest = db.query(WeightEntry).filter(
        WeightEntry.user_id == current_user.id
    ).order_by(desc(WeightEntry.measured_at)).first()

    if latest:
        current_user.current_weight_kg = latest.weight_kg
        db.commit()


# =============================================================================
# Helper Functions
# =============================================================================

def build_history_with_interpolation(
    entries: List[WeightEntry],
    start_date: date,
    end_date: date
) -> List[WeightHistoryPoint]:
    """
    Build weight history with interpolated points for gaps.

    LEARNING NOTE:
    For gaps in data (days without entries), we create interpolated points.
    The frontend draws these as dotted lines instead of solid lines.

    Example:
    - Day 1: 85kg (actual) -> solid
    - Day 2: no entry -> 84.5kg interpolated (dotted)
    - Day 3: 84kg (actual) -> solid
    """
    if not entries:
        return []

    history = []

    # Convert entries to dict for quick lookup
    entry_map = {e.measured_at: e.weight_kg for e in entries}

    # Find actual min/max dates from entries
    min_date = min(e.measured_at for e in entries)
    max_date = max(e.measured_at for e in entries)

    # Iterate through each day in range
    current_date = min_date
    prev_weight = None
    prev_date = None

    while current_date <= max_date:
        if current_date in entry_map:
            # Actual entry
            weight = entry_map[current_date]
            history.append(WeightHistoryPoint(
                date=current_date,
                weight_kg=weight,
                is_interpolated=False
            ))
            prev_weight = weight
            prev_date = current_date
        else:
            # Gap - need to interpolate
            # Find next actual entry
            next_date = current_date + timedelta(days=1)
            next_weight = None

            while next_date <= max_date:
                if next_date in entry_map:
                    next_weight = entry_map[next_date]
                    break
                next_date += timedelta(days=1)

            if prev_weight is not None and next_weight is not None:
                # Linear interpolation
                days_since_prev = (current_date - prev_date).days
                total_days = (next_date - prev_date).days
                if total_days > 0:
                    weight_change = next_weight - prev_weight
                    interpolated_weight = prev_weight + (weight_change * days_since_prev / total_days)
                    history.append(WeightHistoryPoint(
                        date=current_date,
                        weight_kg=round(interpolated_weight, 1),
                        is_interpolated=True
                    ))

        current_date += timedelta(days=1)

    return history


def compute_weight_stats(user: User, entries: List[WeightEntry]) -> WeightStats:
    """
    Compute weight progress statistics.

    LEARNING NOTE:
    These stats appear above the weight graph to show progress at a glance.
    """
    if not entries:
        return WeightStats(
            starting_weight_kg=user.starting_weight_kg,
            current_weight_kg=user.current_weight_kg,
            goal_weight_kg=user.goal_weight_kg,
        )

    starting = user.starting_weight_kg or entries[0].weight_kg
    current = entries[-1].weight_kg  # Most recent entry
    goal = user.goal_weight_kg

    total_lost = None
    remaining = None
    progress = None

    if starting and current:
        total_lost = round(starting - current, 1)

    if current and goal:
        remaining = round(current - goal, 1)

    if starting and goal and current:
        total_to_lose = starting - goal
        if total_to_lose > 0:
            progress = round(((starting - current) / total_to_lose) * 100, 1)
            progress = max(0, min(100, progress))  # Clamp to 0-100

    return WeightStats(
        starting_weight_kg=starting,
        current_weight_kg=current,
        goal_weight_kg=goal,
        total_lost_kg=total_lost,
        remaining_kg=remaining,
        progress_percent=progress,
    )


def detect_stall(db: Session, user: User) -> StallStatus:
    """
    Detect if user is in a weight stall.

    LEARNING NOTE:
    Stall detection rules (from conversation):
    - Look at last 14 days
    - Need at least 4 entries in that period to detect
    - If weight change is ≤ 0.5kg = stall
    - If fewer than 4 entries, can't detect - nudge user to log more

    A stall means it's time to drop to the next diet level.
    """
    # Look at last 14 days
    end_date = date.today()
    start_date = end_date - timedelta(days=14)

    entries = db.query(WeightEntry).filter(
        WeightEntry.user_id == user.id,
        WeightEntry.measured_at >= start_date,
        WeightEntry.measured_at <= end_date
    ).order_by(WeightEntry.measured_at).all()

    entry_count = len(entries)
    min_entries = 4

    # Not enough data to detect
    if entry_count < min_entries:
        return StallStatus(
            can_detect=False,
            is_stalled=False,
            entries_in_period=entry_count,
            min_entries_needed=min_entries,
            weight_change_kg=None,
            message=f"Log at least {min_entries - entry_count} more weights this week for stall detection. Try weighing in daily!"
        )

    # Calculate weight change
    first_weight = entries[0].weight_kg
    last_weight = entries[-1].weight_kg
    weight_change = last_weight - first_weight  # Negative = loss

    # Stall threshold: ±0.5kg
    is_stalled = abs(weight_change) <= 0.5

    if is_stalled:
        message = "Dein Gewicht stagniert. Erwäge, auf das nächstniedrigere Kalorienlevel zu wechseln."
    elif weight_change < 0:
        message = f"Super Fortschritt! Du hast {abs(weight_change):.1f} kg in den letzten 2 Wochen verloren."
    else:
        message = f"Du hast {weight_change:.1f} kg zugenommen. Kein Problem — bleib bei deinem aktuellen Kalorienlevel."

    return StallStatus(
        can_detect=True,
        is_stalled=is_stalled,
        entries_in_period=entry_count,
        min_entries_needed=min_entries,
        weight_change_kg=round(weight_change, 1),
        message=message,
    )
