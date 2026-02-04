"""
Weight Tracking Schemas - API Request/Response Models

LEARNING NOTE:
These schemas handle weight entry CRUD and provide:
1. Creating/updating weight entries
2. Returning weight history with computed stats
3. Stall detection results

The frontend will use these to build an Apple Health-style weight graph.

TUTORIAL: https://fastapi.tiangolo.com/tutorial/response-model/
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime


# =============================================================================
# Weight Entry Schemas
# =============================================================================

class WeightEntryCreate(BaseModel):
    """
    Create a new weight entry.

    LEARNING NOTE:
    - measured_at: The date the weight was measured (user picks date)
    - weight_kg: Weight in kilograms (ISO units only for MVP)
    - notes: Optional context like "after vacation" or "morning"
    """
    weight_kg: float = Field(..., ge=30, le=300, description="Weight in kg (30-300)")
    measured_at: date = Field(..., description="Date of measurement")
    notes: Optional[str] = Field(None, max_length=200, description="Optional notes")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "weight_kg": 82.5,
                    "measured_at": "2026-02-03",
                    "notes": "Morning weight"
                }
            ]
        }
    }


class WeightEntryUpdate(BaseModel):
    """
    Update an existing weight entry.
    All fields optional - only provided fields are updated.
    """
    weight_kg: Optional[float] = Field(None, ge=30, le=300)
    measured_at: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=200)


class WeightEntryResponse(BaseModel):
    """
    Response for a single weight entry.
    """
    id: str
    weight_kg: float
    measured_at: date
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# Weight History & Stats Schemas
# =============================================================================

class WeightHistoryPoint(BaseModel):
    """
    A single point on the weight graph.

    LEARNING NOTE:
    - is_interpolated: True if this is a dotted line (no actual measurement)
    - This allows the frontend to draw solid vs dotted lines
    """
    date: date
    weight_kg: float
    is_interpolated: bool = False  # True for gaps (dotted lines)


class WeightStats(BaseModel):
    """
    Computed statistics for the user's weight progress.

    LEARNING NOTE:
    These stats help show progress at a glance in the app.
    """
    starting_weight_kg: Optional[float] = None
    current_weight_kg: Optional[float] = None
    goal_weight_kg: Optional[float] = None
    total_lost_kg: Optional[float] = None
    remaining_kg: Optional[float] = None
    progress_percent: Optional[float] = None  # 0-100


class StallStatus(BaseModel):
    """
    Stall detection result.

    LEARNING NOTE:
    A "stall" in Faultierdiät means weight hasn't changed significantly
    for 2+ weeks despite following the plan. This signals time to drop
    to the next level (more calorie restriction).

    Requirements for stall detection:
    - At least 4 entries in the last 14 days
    - Weight change ≤ 0.5kg over that period = stall
    - Fewer than 4 entries = can't detect, show nudge message
    """
    can_detect: bool  # False if not enough data
    is_stalled: bool = False
    entries_in_period: int = 0
    min_entries_needed: int = 4
    weight_change_kg: Optional[float] = None
    message: str  # User-friendly message


class WeightHistoryResponse(BaseModel):
    """
    Complete weight history response.

    LEARNING NOTE:
    This powers the main weight graph screen.
    - history: Points for the graph (includes interpolated points for gaps)
    - stats: Summary numbers shown above/below graph
    - stall_status: Whether user is stalled and should level down
    - entries: Raw entries for editing
    """
    history: List[WeightHistoryPoint]
    stats: WeightStats
    stall_status: StallStatus
    entries: List[WeightEntryResponse]  # Raw entries for CRUD operations

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "history": [
                        {"date": "2026-01-20", "weight_kg": 85.0, "is_interpolated": False},
                        {"date": "2026-01-21", "weight_kg": 84.8, "is_interpolated": True},
                        {"date": "2026-01-22", "weight_kg": 84.5, "is_interpolated": False}
                    ],
                    "stats": {
                        "starting_weight_kg": 85.0,
                        "current_weight_kg": 82.5,
                        "goal_weight_kg": 75.0,
                        "total_lost_kg": 2.5,
                        "remaining_kg": 7.5,
                        "progress_percent": 25.0
                    },
                    "stall_status": {
                        "can_detect": True,
                        "is_stalled": False,
                        "entries_in_period": 6,
                        "min_entries_needed": 4,
                        "weight_change_kg": -1.2,
                        "message": "Great progress! Keep going."
                    },
                    "entries": []
                }
            ]
        }
    }
